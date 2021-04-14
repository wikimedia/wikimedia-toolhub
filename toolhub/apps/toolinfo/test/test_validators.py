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
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from ..validators import validate_language_code
from ..validators import validate_language_code_list
from ..validators import validate_spdx
from ..validators import validate_url_mutilingual
from ..validators import validate_url_mutilingual_list


class ValidatorsTest(SimpleTestCase):
    """Test validators."""

    def test_validate_language_code_valid(self):
        """Valid language codes are valid."""
        validate_language_code("en")
        validate_language_code("fr")
        validate_language_code("ady-cyrl")

    def test_validate_language_code_invalid(self):
        """Invalid language codes are invalid."""
        with self.assertRaises(ValidationError):
            validate_language_code("")
        with self.assertRaises(ValidationError):
            validate_language_code("*")
        with self.assertRaises(ValidationError):
            validate_language_code("en-us")

    def test_validate_language_code_list(self):
        """Validate lists of codes."""
        validate_language_code_list(["en"])
        validate_language_code_list(["fj", "ady-cyrl"])

        with self.assertRaises(ValidationError):
            validate_language_code_list(None)
        with self.assertRaises(ValidationError):
            validate_language_code_list("en")
        with self.assertRaises(ValidationError):
            validate_language_code_list(["*", "en"])

    def test_validate_spdx_valid(self):
        """Valid SPDX id are valid."""
        validate_spdx("0BSD")
        validate_spdx("GPL-3.0-or-later")
        validate_spdx("AGPL-3.0-or-later")
        validate_spdx("CC-BY-SA-4.0")

    def test_validate_spdx_invalid(self):
        """Invalid SPDX id are invalid."""
        with self.assertRaises(ValidationError):
            validate_spdx("")
        with self.assertRaises(ValidationError):
            validate_spdx(None)
        with self.assertRaises(ValidationError):
            validate_spdx("bd808-general-license")

    def test_validate_url_multilingual_valid(self):
        """Valid url_multilingual values are valid."""
        validate_url_mutilingual(
            {"url": "https://example.org", "language": "en"}
        )
        validate_url_mutilingual(
            {"url": "http://example.net", "language": "ady-cyrl"}
        )

    def test_validate_url_multilingual_invalid(self):
        """Invalid url_multilingual values are invalid."""
        with self.assertRaises(ValidationError):
            validate_url_mutilingual(None)
        with self.assertRaises(ValidationError):
            validate_url_mutilingual("")
        with self.assertRaises(ValidationError):
            validate_url_mutilingual({})
        with self.assertRaises(ValidationError):
            validate_url_mutilingual({"url": "https://example.org"})
        with self.assertRaises(ValidationError):
            validate_url_mutilingual({"language": "en"})
        with self.assertRaises(ValidationError):
            validate_url_mutilingual(
                {"url": "https://example.org", "language": "invalid"}
            )
        with self.assertRaises(ValidationError):
            validate_url_mutilingual({"url": "example.org", "language": "en"})

    def test_validate_url_multilingual_list_valid(self):
        """Valid url_multilingual value lists are valid."""
        validate_url_mutilingual_list(
            [
                {"url": "https://example.org", "language": "en"},
                {"url": "http://example.net", "language": "ady-cyrl"},
            ]
        )

    def test_validate_url_multilingual_list_invalid(self):
        """Invalid url_multilingual value lists are invalid."""
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list(None)
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list([None])
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list([""])
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list([{}])
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list([{"url": "https://example.org"}])
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list([{"language": "en"}])
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list(
                [
                    {"url": "https://example.org", "language": "invalid"},
                ]
            )
        with self.assertRaises(ValidationError):
            validate_url_mutilingual_list(
                [
                    {"url": "example.org", "language": "en"},
                ]
            )
