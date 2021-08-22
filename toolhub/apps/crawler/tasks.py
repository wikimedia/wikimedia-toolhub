# Copyright (c) 2021 Wikimedia Foundation and contributors.
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

from django.core.exceptions import ValidationError
from django.db import Error
from django.utils import timezone

import requests

from toolhub.apps.auditlog.context import auditlog_context
from toolhub.apps.toolinfo.models import Tool

from .logging import CaptureCrawlLogs
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
        names_seen_in_run = {}

        for url in self.get_active_urls():
            # FIXME: rate limiting for outbound requests?
            run_url = RunUrl(run=run, url=url)
            with CaptureCrawlLogs(run_url):
                self.process_url(run_url, names_seen_in_run)

        run.end_date = timezone.now()
        run.save()
        return run

    def process_url(self, run_url, seen):
        """Crawl a URL and update the run."""
        logger.info("Crawling %s", run_url.url.url)
        expected_names = self.toolinfo_in_last_run(run_url.url)
        toolinfo_list = self.fetch_content(run_url)
        run_url.save()

        for toolinfo in toolinfo_list:
            if not self.validate_toolinfo(toolinfo):
                if run_url.valid:
                    # Mark URL as invalid if any of it's contained tools is
                    # invalid in this run.
                    run_url.valid = False
                    run_url.save()
                continue

            logger.info(
                "Found toolinfo %s at %s",
                toolinfo["name"],
                run_url.url.url,
            )
            if toolinfo["name"] in seen:
                # T278065: Reject updates from multiple urls in same run
                logger.error(
                    "Toolinfo %s already seen at %s",
                    toolinfo["name"],
                    seen[toolinfo["name"]],
                )
                expected_names.discard(toolinfo["name"])
                continue
            seen[toolinfo["name"]] = run_url.url.url

            try:
                obj, created, updated = Tool.objects.from_toolinfo(
                    toolinfo,
                    run_url.url.created_by,
                    Tool.ORIGIN_CRAWLER,
                    "Import from {}".format(run_url.url.url),
                )
                if created:
                    run_url.run.new_tools += 1
                if updated:
                    run_url.run.updated_tools += 1
                run_url.run.total_tools += 1
                run_url.tools.add(obj)
                expected_names.discard(obj.name)

            except (
                Error,
                ValidationError,
            ):
                logger.exception(
                    "Failed to upsert `%s` from %s",
                    toolinfo["name"],
                    run_url.url.url,
                )
                run_url.valid = False
                run_url.save()

        if len(expected_names) > 0:
            logger.info(
                "Expected but did not find toolinfo: %s", expected_names
            )
            if 200 <= run_url.status_code <= 299 or run_url.status_code == 404:
                # T271128: delete missing tools
                reason = "Toolinfo removed from {}"
                if run_url.status_code == 404:
                    reason = "Url {} not found during crawl"
                try:
                    with auditlog_context(
                        run_url.url.created_by, reason.format(run_url.url.url)
                    ):
                        Tool.objects.filter(name__in=expected_names).delete()
                except Error:
                    logger.exception(
                        "Failed to delete missing tools: %s", expected_names
                    )

    def toolinfo_in_last_run(self, url):
        """Find the toolinfo records in the most recent run for a url."""
        expected = set()
        last_run = url.crawler_runs.order_by("-id").first()
        if last_run:
            qs = last_run.tools.filter(deleted__isnull=True).distinct()
            expected.update(qs.values_list("name", flat=True))
        return expected

    def validate_toolinfo(self, toolinfo):
        """Determine if a record is valid."""
        is_valid = True
        # FIXME: do a more complete job of validating the record
        for field in ["name", "title", "description", "url"]:
            if field not in toolinfo or not toolinfo[field]:
                logger.error(
                    "Toolinfo record %s missing %s.",
                    toolinfo.get("name", ""),
                    field,
                )
                is_valid = False
        return is_valid

    def get_active_urls(self):
        """Get all URLs ready for crawling."""
        # FIXME: filter out "failed" urls?
        return Url.objects.all()

    def fetch_content(self, url):
        """Crawl a URL and return it's content."""
        raw_url = url.url.url
        url.status_code = 999
        try:
            r = requests.get(
                raw_url,
                headers={"user-agent": self.user_agent},
                # T288536: 5s connect, 13s read (time between bytes)
                timeout=(5, 13),
            )

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

        except requests.ConnectTimeout:
            logger.exception("Timeout connecting to %s", raw_url)
            r = "Connect Timeout"

        except requests.ReadTimeout:
            logger.exception("Timeout reading response bytes from %s", raw_url)
            r = "Read Timeout"

        except requests.RequestException as e:
            logger.exception("Error crawling url %s", raw_url)
            r = str(e)

        logger.error("Failed to fetch %s: %s", url.url, r)
        return []
