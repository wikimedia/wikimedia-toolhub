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
from django.test import SimpleTestCase

from .. import schema


class SchemaTest(SimpleTestCase):
    """Test schema helpers."""

    @classmethod
    def setUpClass(cls):
        """Setup for all tests in this TestCase."""
        super().setUpClass()
        cls.fixture = schema.load_schema(schema.CURRENT_SCHEMA)

    def test_resolve_ref(self):
        """Happy path test of resolving a ref."""
        self.assertEqual(
            schema.resolve_ref(self.fixture, "#/definitions/url"),
            self.fixture["definitions"]["url"],
        )
        self.assertEqual(
            schema.resolve_ref(
                self.fixture,
                "#/definitions/tool/properties/name/examples/0",
            ),
            self.fixture["definitions"]["tool"]["properties"]["name"][
                "examples"
            ][0],
        )

    def test_expand_refs(self):
        """Expand refs."""
        self.assertEqual(schema.expand_refs({}, {}), {})
        self.assertEqual(schema.expand_refs([], {}), [])
        self.assertEqual(schema.expand_refs("foo", {}), "foo")

        defs = self.fixture["definitions"]
        expect = defs["url"].copy()
        expect["description"] = defs["tool"]["properties"]["url"][
            "description"
        ]
        self.assertEqual(
            schema.expand_refs(
                defs["tool"]["properties"]["url"], self.fixture
            ),
            expect,
        )
