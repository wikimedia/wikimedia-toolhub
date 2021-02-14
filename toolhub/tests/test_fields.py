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

from .. import fields


class JSONSchemaValidatorTest(SimpleTestCase):
    """Test JSONSchemaValidator"""

    def test_valid(self):
        """Valid inputs are valid."""
        fixture = (
            ({"type": "string", "maxLength": 255}, "any old string"),
            ({"type": "array", "items": {"type": "string"}}, ["a", "b"]),
        )

        for schema, value in fixture:
            validator = fields.JSONSchemaValidator(schema)
            try:
                validator(value)
            except ValidationError:
                self.fail(
                    "{} raised ValidationError against {}".format(
                        repr(value), repr(schema)
                    )
                )

    def test_invalid(self):
        """Invalid inputs are invalid."""
        fixture = (
            ({"type": "string", "maxLength": 255}, 1337),
            ({"type": "array", "items": {"type": "string"}}, [13, 37]),
        )

        for schema, value in fixture:
            validator = fields.JSONSchemaValidator(schema)
            self.assertRaisesMessage(
                ValidationError,
                str(fields.JSONSchemaValidator.message),
                validator,
                value,
            )
