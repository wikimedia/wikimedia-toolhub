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
import os

from django.test import TestCase

import requests_mock

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
        urls,
        status_code=200,
        redirected=False,
        valid=True,
    ):
        """Given a RunUrl, check its properties."""
        self.assertEqual(urls.status_code, status_code)
        self.assertEqual(urls.redirected, redirected)
        self.assertEqual(urls.valid, valid)

    def setup_url_fixture(
        self,
        rmock,
        url="http://example.org/toolinfo.json",
        fixture=None,
        **kwargs,
    ):
        """Register a URL to crawl and its expected response."""
        curl = Url.objects.create(url=url, created_by=self.user)

        if fixture:
            fpath = os.path.join(self.work_dir, fixture)
            with open(fpath, "r") as f:
                kwargs["text"] = f.read()

        rmock.register_uri("GET", url, **kwargs)
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
