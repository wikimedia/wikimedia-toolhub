# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Toolhub is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Toolhub.  If not, see <http://www.gnu.org/licenses/>.
import json
import logging

import django.db
from django.utils import timezone

import requests

from toolhub.apps.toolinfo.models import Tool

from .models import Run
from .models import RunUrl
from .models import Url


logger = logging.getLogger(__name__)


class Crawler:
    """Toolinfo URL crawler."""

    def __init__(self):
        """Initialize a new instance."""
        self.user_agent = "Toolhub toolinfo crawler"

    def crawl(self):  # noqa: R0912
        """Crawl all URLs and create/update tool records."""
        logger.info("Starting crawl")
        run = Run()
        run.save()

        for url in self.getActiveUrls():
            # FIXME: rate limiting for outbound requests?
            logger.info("Crawling %s", url)
            run_url = RunUrl(run=run, url=url)
            tools = self.crawlUrl(run_url)
            run_url.save()

            for tool in tools:
                tool_valid = True
                # FIXME: do a more complete job of validating the record
                for field in ["name", "title", "description", "url"]:
                    if field not in tool or not tool[field]:
                        logger.error("Toolinfo record missing %s.", field)
                        tool_valid = False
                if not tool_valid:
                    if run_url.valid:
                        # Mark URL as invalid if any of it's contained tools
                        # is invalid in this run.
                        run_url.valid = False
                        run_url.save()
                    continue

                logger.info("Found tool `%s`", tool["name"])

                try:
                    obj, created, updated = Tool.objects.from_toolinfo(
                        tool, url.created_by
                    )
                    if created:
                        run.new_tools += 1
                    if updated:
                        run.updated_tools += 1
                    run.total_tools += 1
                    run_url.tools.add(obj)

                except django.db.Error:
                    logger.exception(
                        "Failed to upsert `%s` from %s",
                        tool["name"],
                        run_url.url.url,
                    )
                    run_url.valid = False
                    run_url.save()

        run.end_date = timezone.now()
        run.save()
        return run

    def getActiveUrls(self):
        """Get all URLs ready for crawling."""
        # FIXME: filter out "failed" urls?
        return Url.objects.all()

    def crawlUrl(self, url):
        """Crawl a URL and return it's content."""
        raw_url = url.url.url
        r = requests.get(raw_url, headers={"user-agent": self.user_agent})
        url.status_code = r.status_code
        if r.history:
            url.redirected = True
        url.elapsed_ms = r.elapsed.microseconds
        if r.ok:
            try:
                tools = r.json()
                # FIXME: validate schema for entire file?
                url.valid = True
                if not isinstance(tools, list):
                    tools = [tools]
                return tools
            except json.decoder.JSONDecodeError:
                logger.exception("Failed to parse JSON from %s", raw_url)
                url.valid = False
                return []

        logger.error("Failed to fetch %s: %s", url.url, r)
        return []
