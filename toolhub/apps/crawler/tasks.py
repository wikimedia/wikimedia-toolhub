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

from .models import CrawledUrl
from .models import CrawlerRun
from .models import CrawlerRunUrl


logger = logging.getLogger(__name__)


class Crawler:
    """Toolinfo URL crawler."""

    def __init__(self):
        """Initialize a new instance."""
        self.user_agent = "Toolhub toolinfo crawler"

    def crawl(self):
        """Crawl all URLs and create/update tool records."""
        logger.info("Starting crawl")
        run = CrawlerRun()
        run.save()

        for url in self.getActiveUrls():
            # FIXME: rate limiting for outbound requests?
            logger.info("Crawling %s", url)
            crawl_url = CrawlerRunUrl(run=run, url=url)
            tools = self.crawlUrl(crawl_url)
            crawl_url.save()

            for tool in tools:
                # FIXME: do a more complete job of validating the record
                for field in ["name", "title", "description", "url"]:
                    if field not in tool or not tool[field]:
                        logger.error("Toolinfo record missing %s.", field)
                        crawl_url.valid = False
                if not crawl_url.valid:
                    crawl_url.save()
                    continue

                logger.info("Found tool `%s`", tool["name"])

                tool["created_by"] = url.created_by
                tool["modified_by"] = url.created_by

                if "$schema" in tool:
                    tool["_schema"] = tool.pop("$schema")

                if "$language" in tool:
                    tool["_language"] = tool.pop("$language")

                try:
                    # FIXME: what should we do if we get duplicates from
                    # multiple source URLs? This can happen for example if
                    # a Toolforge tool is registered independent of the
                    # Striker managed toolinfo record.
                    obj, created = Tool.objects.update_or_create(
                        name=tool["name"],
                        defaults=tool,
                    )
                    if created:
                        run.new_tools += 1
                    crawl_url.tools.add(obj)

                except django.db.Error:
                    logger.exception(
                        "Failed to upsert `%s` from %s",
                        tool["name"],
                        crawl_url.url.url,
                    )
                    crawl_url.valid = False
                    crawl_url.save()

        run.end_date = timezone.now()
        run.save()
        return run

    def getActiveUrls(self):
        """Get all URLs ready for crawling."""
        # FIXME: filter out "failed" urls?
        return CrawledUrl.objects.all()

    def crawlUrl(self, url):
        """Crawl an URL and return it's content."""
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
