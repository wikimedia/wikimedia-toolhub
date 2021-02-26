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

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

import reversion
from reversion.models import Version

from toolhub.apps.user.models import ToolhubUser

from .. import models
from .. import views


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class ToolRevisionViewSetTest(TestCase):
    """Test ToolRevisionViewSet."""

    @classmethod
    def versions(cls, tool=None):
        """Get queryset over versions."""
        if tool is None:
            tool = cls.tool
        return Version.objects.get_for_object(tool)

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

        cls.tool, _, _ = models.Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, models.Tool.ORIGIN_API
        )

    def test_list(self):
        """Test list action."""
        req = APIRequestFactory().get("")
        view = views.ToolRevisionViewSet.as_view({"get": "list"})
        response = view(req, tool_name=self.tool.name)
        self.assertEqual(response.status_code, 200)

    def test_retrieve(self):
        """Test retrieve action."""
        req = APIRequestFactory().get("")
        view = views.ToolRevisionViewSet.as_view({"get": "retrieve"})
        response = view(
            req, pk=self.versions().first().pk, tool_name=self.tool.name
        )
        self.assertEqual(response.status_code, 200)

    def test_diff(self):
        """Test diff action."""
        with reversion.create_revision():
            self.tool.title = "Changed"
            self.tool.save()

        req = APIRequestFactory().get("")
        view = views.ToolRevisionViewSet.as_view({"get": "diff"})
        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk
        self.assertNotEqual(diff_from, diff_to)
        response = view(
            req,
            pk=diff_from,
            other_id=diff_to,
            tool_name=self.tool.name,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("original", response.data)
        self.assertIn("operations", response.data)
        self.assertIn("result", response.data)

    def test_revert_requires_auth(self):
        """Test revert action."""
        req = APIRequestFactory().post("")
        view = views.ToolRevisionViewSet.as_view({"post": "revert"})
        response = view(
            req,
            pk=self.versions().last().pk,
            tool_name=self.tool.name,
        )
        self.assertEqual(response.status_code, 401)

    def test_revert(self):
        """Test revert action."""
        with reversion.create_revision():
            self.tool.title = "Changed"
            self.tool.save()
        self.assertEqual(self.tool.title, "Changed")

        req = APIRequestFactory().post("")
        force_authenticate(req, user=self.user)
        view = views.ToolRevisionViewSet.as_view({"post": "revert"})
        response = view(
            req,
            pk=self.versions().last().pk,
            tool_name=self.tool.name,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_requires_auth(self):
        """Test undo action."""
        req = APIRequestFactory().post("")
        view = views.ToolRevisionViewSet.as_view({"post": "undo"})
        response = view(
            req,
            pk=self.versions().first().pk,
            other_id=self.versions().last().pk,
            tool_name=self.tool.name,
        )
        self.assertEqual(response.status_code, 401)

    def test_undo(self):
        """Test undo action."""
        with reversion.create_revision():
            self.tool.title = "Changed"
            self.tool.save()
        self.assertEqual(self.tool.title, "Changed")

        req = APIRequestFactory().post("")
        force_authenticate(req, user=self.user)
        view = views.ToolRevisionViewSet.as_view({"post": "undo"})
        undo_from = self.versions().first().pk
        undo_to = self.versions().last().pk
        self.assertNotEqual(undo_from, undo_to)
        response = view(
            req,
            pk=undo_from,
            other_id=undo_to,
            tool_name=self.tool.name,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_invalid(self):
        """Test undo action."""
        with reversion.create_revision():
            self.tool.technology_used = []
            self.tool.save()
        self.assertEqual(self.tool.technology_used, [])

        req = APIRequestFactory().post("")
        force_authenticate(req, user=self.user)
        view = views.ToolRevisionViewSet.as_view({"post": "undo"})
        # Prepare an undo that tries to empty an already empty array
        undo_from = self.versions().last().pk
        undo_to = self.versions().first().pk
        self.assertNotEqual(undo_from, undo_to)
        response = view(
            req,
            pk=undo_from,
            other_id=undo_to,
            tool_name=self.tool.name,
        )
        self.assertEqual(response.status_code, 409)