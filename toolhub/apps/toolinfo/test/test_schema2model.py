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
from django.test import SimpleTestCase

from .. import schema2model


class Schema2ModelTest(SimpleTestCase):
    """Test model generation helper script."""

    def test_something(self):
        """Assert that foo === foo."""
        self.assertEqual("foo", "foo")

    def test_to_camel_case(self):
        """Validate CamelCase conversions."""
        data = [
            ("foo", "Foo"),
            ("foo_bar", "FooBar"),
            ("foo__bar", "FooBar"),
            ("FOOBAR", "Foobar"),
        ]
        for given, expect in data:
            with self.subTest(given=given, expect=expect):
                self.assertEqual(expect, schema2model.to_camel_case(given))

    def test_to_python_var(self):
        """Validate Python variable name conversions."""
        data = [
            ("foo", "foo"),
            ("foo_bar", "foo_bar"),
            ("foo__bar", "foo__bar"),
            ("FOOBAR", "FOOBAR"),
            ("$schema", "_schema"),
        ]
        for given, expect in data:
            with self.subTest(given=given, expect=expect):
                self.assertEqual(expect, schema2model.to_python_var(given))

    def test_required_args(self):
        """Validate required argument generation."""
        required_fields = ["foo", "bar", "baz"]
        expect_pk = {"primary_key": "True"}
        expect_required = {}
        expect_default = {"null": "True", "blank": "True"}
        data = [
            ("id", expect_pk),
            ("_id", expect_pk),
            ("bar", expect_required),
            ("xyzzy", expect_default),
        ]
        for given, expect in data:
            with self.subTest(given=given, expect=expect):
                self.assertEqual(
                    expect, schema2model.required_args(given, required_fields)
                )
