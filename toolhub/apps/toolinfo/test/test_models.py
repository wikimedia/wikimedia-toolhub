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

    def assertToolBasics(self, obj, toolinfo, origin=None, user=None):
        """Assert that a Tool model matches the given input record."""
        if not origin:  # pragma: no cover
            origin = models.Tool.ORIGIN_CRAWLER
        if not user:  # pragma: no cover
            user = self.user

        self.assertIsInstance(obj, models.Tool)
        slug = models.name_to_slug(toolinfo["name"])
        self.assertEqual(obj.name, slug)
        self.assertEqual(obj.auditlog_label, slug)
        self.assertEqual(obj.created_by, user)
        self.assertEqual(obj.modified_by, user)
        self.assertEqual(obj._schema, toolinfo["$schema"])  # noqa: W0212
        self.assertEqual(obj._language, toolinfo["$language"])  # noqa: W0212
        self.assertEqual(obj.origin, origin)

        for field in models.ToolManager.ARRAY_FIELDS:
            self.assertIsInstance(getattr(obj, field), list)

        for field in models.ToolManager.URL_MULTILINGUAL_FIELDS:
            value = getattr(obj, field)
            for mlurl in value:
                self.assertIsInstance(mlurl, dict)
                self.assertIn("url", mlurl)
                self.assertIn("language", mlurl)

        self.assertIsInstance(obj.keywords, list)
        for kw in obj.keywords:
            self.assertEqual(kw, kw.lower())

    def test_from_toolinfo(self):
        """Happy path test of creating a tool from toolinfo data."""
        fixture = self.toolinfo.copy()
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(obj, self.toolinfo)

    def test_legacy_toolforge_name_fix(self):
        """Names starting with 'toolforge.' are slugified."""
        fixture = self.toolinfo.copy()
        fixture["name"] = "toolforge.some-tool"
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(
            obj, {**self.toolinfo, "name": "toolforge-some-tool"}
        )
        self.assertEqual(obj.name, "toolforge-some-tool")

    def test_url_multilingual_fixups(self):
        """url_multilingual fields should be normalized."""
        fixture = self.toolinfo.copy()
        fixture["$language"] = "*"  # should change to "en"
        fixture["privacy_policy_url"] = [
            {
                "language": "invalid-lang-code",  # should change to "en"
                "url": "https://example.org/invalid_lang",
            },
            {
                "language": "de-ch-foo",  # should change to "de-ch"
                "url": "https://example.org/strip_tag",
            },
            {
                # should have language:en added
                "url": "https://example.org/missing_lang",
            },
            {
                "language": "fj",
                "url": "https://example.org/valid_lang",
            },
            {},  # should be discarded
        ]
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(obj, self.toolinfo)
        self.assertCountEqual(
            obj.developer_docs_url,
            [
                {
                    "language": "en",
                    "url": "https://toolhub.wikimedia.org/static/docs/index.html",
                },
            ],
        )
        self.assertCountEqual(
            obj.privacy_policy_url,
            [
                {"language": "en", "url": "https://example.org/invalid_lang"},
                {"language": "de-ch", "url": "https://example.org/strip_tag"},
                {"language": "en", "url": "https://example.org/missing_lang"},
                {"language": "fj", "url": "https://example.org/valid_lang"},
            ],
        )

    def test_keywords_string_to_array(self):
        """Keywords as a string will convert to an array."""
        fixture = self.toolinfo.copy()
        fixture["keywords"] = "a, b"
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(obj, self.toolinfo)
        self.assertCountEqual(obj.keywords, ["a", "b"])

    def test_allow_keywords_as_array(self):
        """Keywords can be an array in the input."""
        fixture = self.toolinfo.copy()
        fixture["keywords"] = ["a", "b"]
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(obj, self.toolinfo)
        self.assertCountEqual(obj.keywords, ["a", "b"])

    def test_clean_ui_langs(self):
        """Invalid available_ui_languages values are discarded."""
        fixture = self.toolinfo.copy()
        fixture["available_ui_languages"] = ["en", "*", "en", "fj", "de-ch-"]
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(obj, self.toolinfo)
        self.assertCountEqual(
            obj.available_ui_languages, ["en", "fj", "de-ch"]
        )

    def test_unexpected_fields_discarded(self):
        """Unexpected fields in toolinfo.json should be discarded."""
        fixture = self.toolinfo.copy()
        fixture["__test__unexpected__"] = "ignore me!"
        obj, created, updated = models.Tool.objects.from_toolinfo(
            fixture, self.user, models.Tool.ORIGIN_CRAWLER
        )

        self.assertTrue(created)
        self.assertFalse(updated)
        self.assertToolBasics(obj, self.toolinfo)

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
