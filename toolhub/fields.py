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

from django.contrib.staticfiles import finders
from django.core import exceptions

from jsonfield import JSONField

import jsonschema
import jsonschema.exceptions


class JSONSchemaField(JSONField):
    """JSONField with support for jsonschema validation."""

    schema_data = None

    def __init__(self, *args, **kwargs):
        """Initialize object."""
        self.schema_data = kwargs.pop("schema", None)
        super().__init__(*args, **kwargs)

    @property
    def schema(self):
        """Get the validaation schema."""
        if isinstance(self.schema_data, str):
            with open(finders.find(self.schema_data), "r") as f:
                self.schema_data = json.loads(f.read())
        return self.schema_data

    def validate(self, value, model_instance):
        """Validate value and raise ValidationError when invalid."""
        super().validate(value, model_instance)
        try:
            return jsonschema.validate(value, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            raise exceptions.ValidationError(str(e), code="invalid")
