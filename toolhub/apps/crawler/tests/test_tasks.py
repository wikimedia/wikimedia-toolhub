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
import os

from django.test import TestCase

import requests_mock

from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.user.models import ToolhubUser

from .. import tasks
from ..models import Url


@requests_mock.Mocker()
class CrawlerTestCase(TestCase):
    """Test the crawler."""

    def setUp(self):
        """Initialize common test conditions."""
        self.user = ToolhubUser.objects.create(
            username="tester",
            email="tester@example.org",
        )

        self.v0_single = {
            "name": "hay-tools-directory",
            "title": "Tools Directory",
            "description": "Discover Wikimedia-related tools.",
            "url": "http://tools.wmflabs.org/hay/directory",
            "keywords": "tools, search, discoverability",
            "author": "Hay Kranen",
            "repository": "https://github.com/hay/wiki-tools.git",
        }

        self.work_dir = os.path.dirname(os.path.abspath(__file__))

    def assertRunResult(self, run, new=0, urls=0):
        """Given a Run, check its properties."""
        self.assertEqual(run.new_tools, new)
        self.assertEqual(run.urls.count(), urls)

    def assertUrlStatus(
        self,
        url,
        status_code=200,
        redirected=False,
        valid=True,
    ):
        """Given a RunUrl, check its properties."""
        self.assertEqual(url.status_code, status_code)
        self.assertEqual(url.redirected, redirected)
        self.assertEqual(url.valid, valid)

    def assertToolsInUrl(self, url, names):
        """Given a RunUrl, check it's last seen tools."""
        qs = url.tools.filter(deleted__isnull=True).distinct()
        found = set(qs.values_list("name", flat=True))
        self.assertEqual(found, set(names))

    def setup_url_response(
        self,
        rmock,
        url="http://example.org/toolinfo.json",
        fixture=None,
        **kwargs,
    ):
        """Configure a response for a given url."""
        if fixture:
            fpath = os.path.join(self.work_dir, fixture)
            with open(fpath, "r") as f:
                kwargs["text"] = f.read()
        rmock.register_uri("GET", url, **kwargs)

    def setup_url_fixture(
        self,
        rmock,
        url="http://example.org/toolinfo.json",
        fixture=None,
        **kwargs,
    ):
        """Register a URL to crawl and its expected response."""
        curl = Url.objects.create(url=url, created_by=self.user)
        self.setup_url_response(rmock, url=url, fixture=fixture, **kwargs)
        return curl

    def test_happy_path(self, rmock):
        """When all the things work as planned, it works."""
        self.setup_url_fixture(rmock, fixture="crawler_happy_path.json")

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=1, urls=1)
        self.assertUrlStatus(run.urls.all()[0])

    def test_legacy_schema(self, rmock):
        """When we recieve a record built for Hay's Directory, it works."""
        self.setup_url_fixture(rmock, json=[self.v0_single])

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=1, urls=1)
        self.assertUrlStatus(run.urls.all()[0])

    def test_404(self, rmock):
        """When the remote returns a 404, we notice but don't fail."""
        self.setup_url_fixture(rmock, status_code=404)

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=0, urls=1)
        self.assertUrlStatus(
            run.urls.all()[0],
            status_code=404,
            valid=False,
        )

    def test_redirect(self, rmock):
        """When the remote redirects, we follow."""
        self.setup_url_fixture(
            rmock,
            status_code=302,
            headers={
                "Location": "https://example.org/toolinfo.json",
            },
        )
        rmock.register_uri(
            "GET",
            "https://example.org/toolinfo.json",
            json=self.v0_single,
        )

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=1, urls=1)
        self.assertUrlStatus(run.urls.all()[0], redirected=True)

    def test_malformed_json(self, rmock):
        """When the response is not valid json, we notice but don't fail."""
        self.setup_url_fixture(rmock, text="<html><body><p>Not JSON!</p>")

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=0, urls=1)
        self.assertUrlStatus(run.urls.all()[0], valid=False)

    def test_missing_name(self, rmock):
        """When a record is missing its name, we notice but don't fail."""
        self.setup_url_fixture(rmock, json={"invalid": True})

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=0, urls=1)
        self.assertUrlStatus(run.urls.all()[0], valid=False)

    def test_delete_on_subsequent_run(self, rmock):
        """When a toolinfo is removed, we notice and remove the Tool."""
        self.setup_url_fixture(rmock, fixture="crawler_missing_run_1.json")
        crawler = tasks.Crawler()

        run = crawler.crawl()
        self.assertRunResult(run, new=3, urls=1)
        self.assertUrlStatus(run.urls.all()[0])
        self.assertToolsInUrl(
            run.urls.all()[0],
            ["test-delete-1", "test-delete-2", "test-delete-3"],
        )
        self.assertEqual(
            "test-delete-2",
            Tool.objects.get(name="test-delete-2").name,
        )

        self.setup_url_response(rmock, fixture="crawler_missing_run_2.json")

        run = crawler.crawl()
        self.assertRunResult(run, new=0, urls=1)
        self.assertUrlStatus(run.urls.all()[0])
        self.assertToolsInUrl(
            run.urls.all()[0],
            ["test-delete-1", "test-delete-3"],
        )
        self.assertRaises(
            Tool.DoesNotExist,
            lambda: Tool.objects.get(name="test-delete-2"),
        )

    def test_revive_on_subsequent_run(self, rmock):
        """When a deleted toolinfo is found, we notice and restore the Tool."""
        # First run has 3 tools
        self.setup_url_fixture(rmock, fixture="crawler_missing_run_1.json")
        crawler = tasks.Crawler()
        crawler.crawl()
        self.assertEqual(
            "test-delete-2",
            Tool.objects.get(name="test-delete-2").name,
        )

        # Second run has 2 tools
        self.setup_url_response(rmock, fixture="crawler_missing_run_2.json")
        crawler.crawl()
        self.assertRaises(
            Tool.DoesNotExist,
            lambda: Tool.objects.get(name="test-delete-2"),
        )

        # Third run has 3 tools
        self.setup_url_response(rmock, fixture="crawler_missing_run_1.json")
        crawler.crawl()
        self.assertEqual(
            "test-delete-2",
            Tool.objects.get(name="test-delete-2").name,
        )

    def test_first_url_wins(self, rmock):
        """When a tool is present in multiple urls, the first url wins."""
        self.setup_url_fixture(rmock, json=[self.v0_single])
        f2 = self.v0_single.copy()
        f2["author"] = "Not " + self.v0_single["author"]
        self.setup_url_fixture(rmock, url="http://example.net", json=[f2])

        crawler = tasks.Crawler()
        run = crawler.crawl()

        self.assertRunResult(run, new=1, urls=2)
        self.assertUrlStatus(run.urls.all()[0])
        self.assertUrlStatus(run.urls.all()[1])
        self.assertEqual(
            self.v0_single["author"],
            Tool.objects.get(name=self.v0_single["name"]).author,
        )
