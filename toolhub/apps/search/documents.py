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
from django_elasticsearch_dsl.exceptions import VariableLookupError
from django_elasticsearch_dsl.registries import registry

from drf_spectacular.drainage import set_override
from drf_spectacular.plumbing import force_instance

from elasticsearch_dsl import analyzer
from elasticsearch_dsl import token_filter

from rest_framework import serializers

from toolhub.apps.lists.models import ToolList
from toolhub.apps.lists.serializers import SummaryToolSerializer
from toolhub.apps.toolinfo.models import Annotations
from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.toolinfo.serializers import AnnotationsSerializer
from toolhub.apps.user.serializers import UserSerializer
from toolhub.fields import JSONSchemaField
from toolhub.serializers import JSONSchemaField as JSONSchemaFieldSerializer


# Monkey patch django_elasticsearch_dsl.fields.DEDField to work around not
# having django-elasticsearch-dsl@11a7b87 which introduces support for
# non-required fields when exporting a document. That functionality is in
# django-elasticsearch-dsl >=7.2.1.
upstream_get_value_from_instance = fields.DEDField.get_value_from_instance


def our_get_value_from_instance(self, instance, field_value_to_ignore=None):
    """Allow missing values when indexing."""
    try:
        return upstream_get_value_from_instance(
            self,
            instance,
            field_value_to_ignore,
        )
    except VariableLookupError as err:
        if self._required:
            raise err
        return None


fields.DEDField.get_value_from_instance = our_get_value_from_instance
# End monkey patch


JSONSCHEMA_TYPE_TO_DSL = {
    "boolean": fields.BooleanField,
    "integer": fields.LongField,
    "number": fields.DoubleField,
}


SERIALIZER_FIELD_TO_ES_FIELD = {
    serializers.BooleanField: fields.BooleanField,
    serializers.ChoiceField: fields.TextField,
    serializers.DateField: fields.DateField,
    serializers.DateTimeField: fields.DateField,
    serializers.EmailField: fields.TextField,
    serializers.FileField: fields.FileField,
    serializers.FilePathField: fields.KeywordField,
    serializers.FloatField: fields.DoubleField,
    serializers.ImageField: fields.FileField,
    serializers.IntegerField: fields.IntegerField,
    serializers.SlugField: fields.KeywordField,
    serializers.TimeField: fields.LongField,
    serializers.URLField: fields.TextField,
    serializers.UUIDField: fields.KeywordField,
}


# Fields that should have a `copy_to` property added in the generated
# mappings. Key is the field name. Value is the copy_to target field.
# FIXME: it would be nicer to keep this configuration inside of SearchDocument
# subclasses instead of as this global config, but so far we have not found
# a reasonable place to insert the necessary logic to make this happen as
# a post-processing step.
COPY_TO_FIELDS = {
    "available_ui_languages": "x_merged_ui_lang",
    "for_wikis": "x_merged_wiki",
    "tool_type": "x_merged_type",
}


en_stem_filter = token_filter("english", type="stemmer")
gram2_filter = token_filter(
    "gram2_shingle",
    type="shingle",
    max_shingle_size=2,
    min_shingle_size=2,
    output_unigrams=True,
)
gram3_filter = token_filter(
    "gram3_shingle",
    type="shingle",
    max_shingle_size=3,
    min_shingle_size=2,
    output_unigrams=True,
)

exact_analyzer = analyzer(
    "exact_analyzer", tokenizer="standard", filter=["lowercase"]
)

en_analyzer = analyzer(
    "en_analyzer",
    tokenizer="standard",
    filter=["lowercase", en_stem_filter],
)

gram2_analyzer = analyzer(
    "gram2_analyzer",
    tokenizer="standard",
    filter=["lowercase", "stop", gram2_filter],
)

gram3_analyzer = analyzer(
    "gram3_analyzer",
    tokenizer="standard",
    filter=["lowercase", "stop", gram3_filter],
)


def build_string_field(**kwargs):
    """Add Elasticsearch schema customizations to strings."""
    if "fields" not in kwargs:
        kwargs["fields"] = {
            "exact": fields.TextField(analyzer=exact_analyzer),
            "keyword": fields.KeywordField(ignore_above=256),
            "gram2": fields.TextField(analyzer=gram2_analyzer),
            "gram3": fields.TextField(analyzer=gram3_analyzer),
        }
    if "analyzer" not in kwargs:
        kwargs["analyzer"] = en_analyzer
    name = kwargs.get("attr", None)
    if name in COPY_TO_FIELDS:
        kwargs["copy_to"] = COPY_TO_FIELDS[name]
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

    field = JSONSCHEMA_TYPE_TO_DSL[type_](attr=attr)
    if attr in COPY_TO_FIELDS:
        field.copy_to = COPY_TO_FIELDS[attr]
    return field


def build_field_from_serializer_field(name, field):
    """Generate a document field mapping from a serializer field."""
    if isinstance(field, JSONSchemaFieldSerializer):
        return build_field_from_schema(field.model_field.schema, name)

    if isinstance(field, serializers.CharField):
        return build_string_field(attr=name)

    try:
        clazz = SERIALIZER_FIELD_TO_ES_FIELD[field.__class__]
        if issubclass(clazz, serializers.CharField):
            return build_string_field(attr=name)

        field = clazz(attr=name)
        if name in COPY_TO_FIELDS:
            field.copy_to = COPY_TO_FIELDS[name]
        return field
    except KeyError as ex:
        raise RuntimeError(
            "Unknown field type {} for {}".format(
                field.__class__.__name__, name
            )
        ) from ex


def build_field_from_serializer(serializer, attr):
    """Generate a document field mapping from a DRF serializer."""
    properties = {}
    for name, field in force_instance(serializer).fields.items():
        if isinstance(field, serializers.Serializer):
            properties[name] = build_field_from_serializer(field, name)
        else:
            properties[name] = build_field_from_serializer_field(name, field)
    obj = fields.ObjectField(properties=properties, attr=attr)
    # Decorate new field with schema for OpenAPI documentation
    set_override(obj, "field", serializer)
    return obj


class SearchDocument(Document):
    """Extension of django_elasticsearch_dsl.Document.

    Adds support for converting JSONSchemaField members of mapped model into
    typed Elasticsearch fields. Also adds useful Elasticsearch schema
    customizations to typed fields.
    """

    @classmethod
    def to_field(cls, field_name, model_field):
        """Get the es field instance approriate for the model field class."""
        field = None
        if isinstance(model_field, JSONSchemaField):
            field = build_field_from_schema(
                model_field._schema, field_name  # noqa: W0212
            )

        elif isinstance(model_field, (CharField, TextField)):
            field = build_string_field(attr=field_name)

        else:
            field = super().to_field(field_name, model_field)

        if field_name in COPY_TO_FIELDS:
            field.copy_to = COPY_TO_FIELDS[field_name]
        return field


@registry.register_document
class ToolDocument(SearchDocument):
    """Tool Elasticsearch document."""

    annotations = build_field_from_serializer(
        AnnotationsSerializer, "annotations"
    )
    created_by = build_field_from_serializer(UserSerializer, "created_by")
    modified_by = build_field_from_serializer(UserSerializer, "modified_by")

    x_merged_ui_lang = fields.KeywordField(ignore_above=256)
    x_merged_wiki = fields.KeywordField(ignore_above=256)
    x_merged_type = fields.KeywordField(ignore_above=256)

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
            # "annotations",
            "_schema",
            "_language",
            "origin",
            # "created_by",
            "created_date",
            # "modified_by",
            "modified_date",
        ]
        related_models = [Annotations]

    def get_queryset(self):
        """Select related models."""
        return super().get_queryset().select_related("annotations")

    def get_instances_from_related(self, related_instance):
        """Retrieve the Tool from related models."""
        if isinstance(related_instance, Annotations):
            return related_instance.tool


@registry.register_document
class ListDocument(SearchDocument):
    """Tool List Elasticsearch document."""

    tools = build_field_from_serializer(SummaryToolSerializer, "tools")
    created_by = build_field_from_serializer(UserSerializer, "created_by")
    modified_by = build_field_from_serializer(UserSerializer, "modified_by")

    x_merged_type = fields.KeywordField(ignore_above=256)

    class Index:
        """Configure index."""

        name = "toolhub_lists"

    class Django:
        """Configure document."""

        model = ToolList
        fields = [
            "id",
            "title",
            "description",
            "icon",
            "favorites",
            "published",
            "featured",
            "created_date",
            "modified_date",
        ]

    def get_queryset(self):
        """Filter out unpublished lists"""
        return super().get_queryset().filter(published=True)
