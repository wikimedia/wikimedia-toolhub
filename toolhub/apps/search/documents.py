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
from django.db.models import CharField
from django.db.models import TextField

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from drf_spectacular.drainage import set_override

from elasticsearch_dsl import analyzer
from elasticsearch_dsl import token_filter

from toolhub.apps.toolinfo.models import Tool
from toolhub.fields import JSONSchemaField

from . import schema


JSONSCHEMA_TYPE_TO_DSL = {
    "boolean": fields.BooleanField,
    "integer": fields.LongField,
    "number": fields.DoubleField,
}


en_stem_filter = token_filter(type="stemmer", name_or_instance="english")
en_analyzer = analyzer(
    "en_analyzer",
    tokenizer="standard",
    filter=["standard", "lowercase", en_stem_filter],
)
exact_analyzer = analyzer(
    "exact_analyzer",
    tokenizer="standard",
    filter=["standard", "lowercase"],
)


def build_string_field(**kwargs):
    """Add Elasticsearch schema customizations to strings."""
    if "fields" not in kwargs:
        kwargs["fields"] = {
            "exact": fields.TextField(analyzer=exact_analyzer),
            "keyword": fields.KeywordField(ignore_above=256),
        }
    if "analyzer" not in kwargs:
        kwargs["analyzer"] = en_analyzer
    return fields.TextField(**kwargs)


def build_field_from_schema(schema_, attr):
    """Generate a document field mapping from a JSONSchema description."""
    type_ = schema_["type"]
    if type_ == "object":
        properties = {}
        for key, value in schema_["properties"].items():
            properties[key] = build_field_from_schema(value, None)
        obj = fields.ObjectField(properties=properties, attr=attr)
        # Decorate new field with schema for OpenAPI documentation
        set_override(obj, "field", schema_)
        return obj

    if type_ == "array":
        arr = fields.ListField(
            build_field_from_schema(schema_["items"], attr=attr)
        )
        # Decorate new field with schema for OpenAPI documentation
        set_override(arr, "field", schema_)
        return arr

    if type_ == "string":
        return build_string_field(attr=attr)

    return JSONSCHEMA_TYPE_TO_DSL[type_](attr=attr)


class SearchDocument(Document):
    """Extension of django_elasticsearch_dsl.Document.

    Adds support for converting JSONSchemaField members of mapped model into
    typed Elasticsearch fields. Also adds useful Elasticsearch schema
    customizations to typed fields.
    """

    @classmethod
    def to_field(cls, field_name, model_field):
        """Get the es field instance approriate for the model field class."""
        if isinstance(model_field, JSONSchemaField):
            return build_field_from_schema(
                model_field._schema, field_name  # noqa: W0212
            )

        if isinstance(model_field, (CharField, TextField)):
            return build_string_field(attr=field_name)

        return super().to_field(field_name, model_field)


@registry.register_document
class ToolDocument(SearchDocument):
    """Tool Elasticsearch document."""

    created_by = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "username": fields.TextField(),
        }
    )
    set_override(created_by, "field", schema.USER)

    class Index:
        """Configure index."""

        name = "toolhub_tools"

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
            "origin",
            # "created_by",
            "created_date",
            # "modified_by",
            "modified_date",
        ]
