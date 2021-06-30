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
import os

from django.test import TestCase

from rest_framework.test import APIClient

from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.user.models import ToolhubUser

from .. import models


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class ToolListViewSetTest(TestCase):
    """Test ToolListViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )

        with open(os.path.join(TEST_DIR, "toolinfo_fixture.json")) as fixture:
            cls.toolinfo = json.load(fixture)

        cls.tool, _, _ = Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, Tool.ORIGIN_API
        )

        cls.list = models.ToolList.objects.create(
            title="A test fixture list",
            published=True,
            created_by=cls.user,
        )
        models.ToolListItem.objects.create(
            toollist=cls.list,
            tool=cls.tool,
        )

    def test_create_requires_auth(self):
        """Assert that create fails for anon."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/"
        payload = {"title": "test", "tools": []}
        response = client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/"
        payload = {
            "title": "test",
            "tools": [self.tool.name],
            "comment": "test",
        }
        response = client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_validates_tool_names(self):
        """Ensure duplicate and non-existant tool names are rejected."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/"
        payload = {
            "title": "test",
            "tools": [
                "not valid",
                "no-such-tool",
                self.tool.name,
                self.tool.name,
            ],
        }
        response = client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.data)
        errors = response.data["errors"]
        self.assertEqual(len(errors), 2)
        for error in errors:
            self.assertIn("code", error)
            self.assertIn("field", error)
            self.assertIn("message", error)
            self.assertEqual(str(error["field"]), "tools")

    def test_list(self):
        """Test list."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.list.id)
        self.assertIn("tools", results[0])
        self.assertEqual(len(results[0]["tools"]), 1)
        self.assertEqual(results[0]["tools"][0]["name"], self.tool.name)

    def test_retrieve(self):
        """Test retrieve."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{}/".format(self.list.id)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.list.id)
        self.assertIn("tools", response.data)
        self.assertEqual(len(response.data["tools"]), 1)
        self.assertEqual(response.data["tools"][0]["name"], self.tool.name)

    def test_retrieve_ignores_unpublished(self):
        """Ensure that unpublished lists are not shown to non-owners."""
        self.list.published = False
        self.list.save()
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{}/".format(self.list.id)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
