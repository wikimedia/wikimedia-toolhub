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
from unittest import mock

from django.test import SimpleTestCase

from .. import openapi


class OpenApiTest(SimpleTestCase):
    """Test openapi extensions."""

    def test_postprocess_schema_responses(self):
        """Default response is added to schema."""
        result = {
            "paths": {
                "/foo": {
                    "get": {
                        "responses": {},
                    },
                },
            },
            "components": {
                "schemas": {},
            },
        }
        generator = mock.MagicMock(
            spec_set=["registry"],
        )

        output = openapi.postprocess_schema_responses(result, generator)

        generator.registry.register_on_missing.assert_called()
        generator.registry.build.assert_called_once()
        self.assertIn("default", output["paths"]["/foo"]["get"]["responses"])
