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
import json

from drf_spectacular.drainage import set_override

from jsonfield import JSONField

from rest_framework import serializers

from rest_framework_friendly_errors.mixins import FriendlyErrorMessagesMixin

from . import fields


class JSONSchemaField(serializers.ModelField):
    """Serializer for schema validated JSON data."""

    default_error_messages = {
        fields.JSONSchemaValidator.code: fields.JSONSchemaValidator.message,
    }

    def __init__(self, **kwargs):
        """Initialize object."""
        model_field = kwargs["model_field"]
        super().__init__(**kwargs)

        schema = model_field.schema
        if schema:
            set_override(self, "field", schema)

    def get_attribute(self, obj):
        """Get the primitive value for an outgoing instance."""
        return serializers.Field.get_attribute(self, obj)

    def get_value(self, dictionary):
        """Get value to transform to native from incoming primative data."""
        return serializers.JSONField.get_value(self, dictionary)

    def to_internal_value(self, data):
        """Transform the incoming primitive data to a native value."""
        try:
            if getattr(data, "is_json_string", False):
                return json.loads(data)
            json.dumps(data)
        except (TypeError, ValueError):
            self.fail(fields.JSONSchemaValidator.code)
        return data

    def to_representation(self, obj):
        """Transform the outgoing native value to primitive data."""
        return obj


class BlankAsNullCharField(serializers.CharField):
    """CharField that can store empty strings as null."""

    def to_internal_value(self, data):
        """Transform the incoming primitive data to a native value."""
        if self.allow_blank is True and self.allow_null is True and data == "":
            data = None
        return super().to_internal_value(data)


class Serializer(  # noqa: W0223
    FriendlyErrorMessagesMixin, serializers.Serializer
):
    """A Serializer with friendly error support."""


class ModelSerializer(FriendlyErrorMessagesMixin, serializers.ModelSerializer):
    """A ModelSerializer with friendly error support."""

    def __init__(self, *args, **kwargs):
        """Initialize instance."""
        super().__init__(*args, **kwargs)
        self.serializer_field_mapping[JSONField] = serializers.JSONField
        self.serializer_field_mapping[fields.JSONSchemaField] = JSONSchemaField
        self.serializer_field_mapping[
            fields.BlankAsNullCharField
        ] = BlankAsNullCharField
        self.serializer_field_mapping[
            fields.BlankAsNullTextField
        ] = BlankAsNullCharField
