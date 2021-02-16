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
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from toolhub.fields import JSONSchemaField

from .models import Tool


class JSONSchemaDocument(Document):
    """Extension of django_elasticsearch_dsl.Document.

    Adds support for converting JSONSchemaField members of mapped model into
    typed Elasticsearch fields.
    """

    JSONSCHEMA_TYPE_TO_DSL = {
        "boolean": fields.BooleanField,
        "integer": fields.LongField,
        "number": fields.DoubleField,
        "string": fields.TextField,
    }

    @classmethod
    def field_from_schema(cls, schema, attr):
        """Generate a document field mapping from a JSONSchema description."""
        type_ = schema["type"]
        if type_ == "object":
            properties = {}
            for key, value in schema["properties"].items():
                properties[key] = cls.field_from_schema(value, None)
            return fields.ObjectField(properties=properties, attr=attr)

        if type_ == "array":
            return fields.ListField(
                cls.field_from_schema(schema["items"], attr=attr)
            )

        return cls.JSONSCHEMA_TYPE_TO_DSL[type_](attr=attr)

    @classmethod
    def to_field(cls, field_name, model_field):
        """Get the es field instance approriate for the model field class."""
        if isinstance(model_field, JSONSchemaField):
            return cls.field_from_schema(
                model_field._schema, field_name  # noqa: W0212
            )
        return super().to_field(field_name, model_field)


@registry.register_document
class ToolDocument(JSONSchemaDocument):
    """Tool Elasticsearch document."""

    created_by = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "username": fields.TextField(),
        }
    )

    class Index:
        """Configure index."""

        name = "tools"

    class Django:
        """Configure document."""

        model = Tool
        fields = [
            "name",
            "title",
            "description",
            "url",
            "keywords",
            "author",
            "repository",
            "subtitle",
            "openhub_id",
            "url_alternates",
            "bot_username",
            "deprecated",
            "replaced_by",
            "experimental",
            "for_wikis",
            "icon",
            "license",
            "sponsor",
            "available_ui_languages",
            "technology_used",
            "tool_type",
            "api_url",
            "developer_docs_url",
            "user_docs_url",
            "feedback_url",
            "privacy_policy_url",
            "translate_url",
            "bugtracker_url",
            "_schema",
            "_language",
            #  "created_by",
            "created_date",
            # "modified_by",
            "modified_date",
        ]
