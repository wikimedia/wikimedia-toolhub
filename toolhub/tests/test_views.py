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
from http import HTTPStatus

from django.test import TestCase


class HealthzTests(TestCase):
    """Test healthz."""

    def test_get(self):
        """Assert that GET /healthz works."""
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res["content-type"], "application/json")
        self.assertEqual(res.json()["status"], "OK")

    def test_post_denied(self):
        """Assert that POST /healthz is denied."""
        res = self.client.post("/healthz")
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, res.status_code)


class RobotsTxtTests(TestCase):
    """Test robots_txt."""

    def test_get(self):
        """Assert that GET /robots.txt works."""
        res = self.client.get("/robots.txt")
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(res["content-type"], "text/plain")
        lines = res.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    def test_post_denied(self):
        """Assert that POST /robots.txt is denied."""
        res = self.client.post("/robots.txt")
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, res.status_code)
