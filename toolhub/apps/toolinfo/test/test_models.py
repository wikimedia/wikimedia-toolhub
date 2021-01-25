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

from django.core.exceptions import ValidationError
from django.test import TestCase

from toolhub.apps.user.models import ToolhubUser

from .. import models


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class ToolManagerTest(TestCase):
    """Test ToolManager."""

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

    def assertTool(self, obj, toolinfo, origin=None, user=None):
        """Assert that a Tool model matches the given input record."""
        if not origin:  # pragma: no cover
            origin = models.Tool.ORIGIN_CRAWLER
        if not user:  # pragma: no cover
            user = self.user

        self.assertIsInstance(obj, models.Tool)
        slug = models.name_to_slug(toolinfo["name"])
        self.assertEqual(obj.name, slug)
        self.assertEqual(obj.created_by, user)
        self.assertEqual(obj.modified_by, user)
        self.assertEqual(obj._schema, toolinfo["$schema"])  # noqa: W0212
        self.assertEqual(obj._language, toolinfo["$language"])  # noqa: W0212
        self.assertEqual(obj.origin, origin)

    def test_from_toolinfo(self):
        """Happy path test of creating a tool from toolinfo data."""
        fixture = self.toolinfo.copy()
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertTool(obj, self.toolinfo)

    def test_from_toolinfo_origin_change(self):
        """Expect a validation error when changing a Tool's origin."""
        models.Tool.objects.from_toolinfo(
            self.toolinfo.copy(), self.user, models.Tool.ORIGIN_CRAWLER
        )

        try:
            models.Tool.objects.from_toolinfo(
                self.toolinfo.copy(), self.user, models.Tool.ORIGIN_API
            )

        except ValidationError as e:
            self.assertEqual(e.code, "invariant")

        else:
            self.fail(  # pragma: no cover
                msg="Expected changing origin to raise ValidationError"
            )
