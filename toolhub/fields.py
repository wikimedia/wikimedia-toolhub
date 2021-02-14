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
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from jsonfield import JSONField

import jsonschema
import jsonschema.exceptions
import jsonschema.validators


@deconstructible
class JSONSchemaValidator:
    """Validate against a JSON schema."""

    schema = None
    message = _("Enter a valid value conforming to the JSON Schema.")
    code = 3101

    def __init__(self, schema, message=None, code=None):
        """Initialize instance.

        :param schema: JSON schema to validate against
        :type schema: Union[str, Mapping]
        """
        self.schema = schema
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    @cached_property
    def _schema_validator(self):
        """Get a compiled validator for our schema."""
        if isinstance(self.schema, str):
            with open(finders.find(self.schema), "r") as f:
                self.schema = json.loads(f.read())
        clazz = jsonschema.validators.validator_for(self.schema)
        clazz.check_schema(self.schema)
        return clazz(self.schema)

    def __call__(self, value):
        """Validate that the input matches the JSON schema."""
        try:
            return self._schema_validator.validate(value)

        except jsonschema.exceptions.ValidationError as e:
            raise exceptions.ValidationError(
                self.message, code=self.code
            ) from e

    def __eq__(self, other):
        return (
            isinstance(other, JSONSchemaValidator)
            and (self.schema == other.schema)
            and (self.message == other.message)
            and (self.code == other.code)
        )


class JSONSchemaField(JSONField):
    """JSONField with support for jsonschema validation."""

    _schema = None

    def __init__(self, *args, **kwargs):
        """Initialize object."""
        schema = kwargs.pop("schema", None)
        super().__init__(*args, **kwargs)
        if schema is not None:
            self._schema = schema
            self.validators.append(JSONSchemaValidator(schema))

    @property
    def schema(self):
        """Get the validation schema."""
        if isinstance(self._schema, str):
            with open(finders.find(self._schema), "r") as f:
                self._schema = json.loads(f.read())
        return self._schema
