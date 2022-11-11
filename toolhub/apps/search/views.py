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
from django.utils.translation import gettext_lazy as _

from django_elasticsearch_dsl_drf import constants
from django_elasticsearch_dsl_drf import filter_backends
from django_elasticsearch_dsl_drf import pagination
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from .documents import ListDocument
from .documents import ToolDocument
from .schema import FACET_RESPONSE
from .serializers import AutoCompleteListDocumentSerializer
from .serializers import AutoCompleteToolDocumentSerializer
from .serializers import ListDocumentSerializer
from .serializers import ToolDocumentSerializer


class QueryStringFilterBackend(  # noqa: W0223
    filter_backends.BaseSearchFilterBackend
):
    """Custom search filter backend."""

    matching = constants.MATCHING_OPTION_MUST
    query_backends = [
        filter_backends.search.query_backends.SimpleQueryStringQueryBackend,
    ]


class CustomMultiMatchSearchFilterBackend(
    filter_backends.MultiMatchSearchFilterBackend
):
    """Custom multi-match search filter backend"""

    search_param = "q"


query_param_q = OpenApiParameter(
    "q",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description=_("""Search string"""),
)


class Pagination(pagination.QueryFriendlyPageNumberPagination):
    """Custom pagination for OpenAPI response generation."""

    def get_paginated_response_schema(self, schema):
        """Add facets to schema."""
        schema = super().get_paginated_response_schema(schema)
        return {
            "type": "object",
            "properties": {
                "count": schema["properties"]["count"],
                "next": schema["properties"]["next"],
                "previous": schema["properties"]["previous"],
                "facets": FACET_RESPONSE,
                "results": schema["properties"]["results"],
            },
            "required": ["count", "next", "previous", "results"],
        }


def build_term_filter_field(term):
    """Build filter_fields configuration for a term field.

    :param term: Term field name
    """
    return {
        "field": term,
        "lookups": [
            constants.LOOKUP_FILTER_TERM,
            constants.LOOKUP_QUERY_ISNULL,
        ],
    }


def build_term_facet_options(term, missing="--", multi=False):
    """Build options for a term facet.

    :param term: Term field name
    :param missing: Value to return for douments missing values
    :param multi: Are there multiple values per document?
    """
    return {
        "meta": {
            "type": "terms",
            "param": "{}__term".format(term),
            "missing_value": missing,
            "missing_param": "{}__isnull".format(term),
            "multi": multi,
        },
        "missing": missing,
    }


@extend_schema_view(
    retrieve=extend_schema(
        exclude=True,
    ),
    list=extend_schema(
        description=_("""Autocomplete for tools."""),
        parameters=[query_param_q],
    ),
)
class AutoCompleteToolDocumentViewSet(BaseDocumentViewSet):
    """Tools Auto-complete Search."""

    document = ToolDocument
    document_uid_field = "name"
    serializer_class = AutoCompleteToolDocumentSerializer
    pagination_class = None
    lookup_field = "name"
    filter_backends = [
        filter_backends.DefaultOrderingFilterBackend,
        CustomMultiMatchSearchFilterBackend,
    ]
    multi_match_search_fields = (
        "name",
        "name.gram2",
        "name.gram3",
        "title",
        "title.gram2",
        "title.gram3",
    )
    multi_match_options = {"type": "phrase_prefix"}

    ordering = "title.keyword"


@extend_schema_view(
    retrieve=extend_schema(
        exclude=True,
    ),
    list=extend_schema(
        description=_("""Faceted search for tools."""),
    ),
)
class ToolDocumentViewSet(BaseDocumentViewSet):
    """Tools Full text search."""

    document = ToolDocument
    document_uid_field = "name"
    serializer_class = ToolDocumentSerializer
    pagination_class = Pagination
    filter_backends = [
        QueryStringFilterBackend,
        filter_backends.DefaultOrderingFilterBackend,
        filter_backends.FacetedSearchFilterBackend,
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
    ]
    # Copy searchable fields list from document so we don't have two lists to
    # keep in sync between the index and this view.
    simple_query_string_search_fields = tuple(ToolDocument.Django.fields)
    simple_query_string_options = {
        "analyze_wildcard": True,
        "lenient": True,
        "quote_field_suffix": ".exact",
    }

    filter_fields = {
        "name": {
            "field": "name",
            "lookups": constants.STRING_LOOKUP_FILTERS,
        },
        "wiki": build_term_filter_field("x_merged_wiki"),
        "tool_type": build_term_filter_field("x_merged_type"),
        "author": build_term_filter_field("author.name.keyword"),
        "license": build_term_filter_field("license.keyword"),
        "ui_language": build_term_filter_field("x_merged_ui_lang"),
        "keywords": build_term_filter_field("keywords.keyword"),
        "origin": build_term_filter_field("origin.keyword"),
        "audiences": build_term_filter_field("annotations.audiences.keyword"),
        "content_types": build_term_filter_field(
            "annotations.content_types.keyword"
        ),
        "tasks": build_term_filter_field("annotations.tasks.keyword"),
        "subject_domains": build_term_filter_field(
            "annotations.subject_domains.keyword"
        ),
    }
    ordering_fields = {
        "score": "_score",
        "name": "name.keyword",
        "title": "title.keyword",
        "created_date": "created_date",
        "modified_date": "modified_date",
    }
    ordering = ("_score", "-created_date", "name.keyword")
    faceted_search_fields = {
        "wiki": {
            "field": "x_merged_wiki",
            "options": build_term_facet_options("wiki", multi=True),
            "enabled": True,
        },
        "tool_type": {
            "field": "x_merged_type",
            "options": build_term_facet_options("tool_type"),
            "enabled": True,
        },
        "author": {
            "field": "author.name.keyword",
            "options": build_term_facet_options("author"),
            "enabled": True,
        },
        "license": {
            "field": "license.keyword",
            "options": build_term_facet_options("license"),
            "enabled": True,
        },
        "ui_language": {
            "field": "x_merged_ui_lang",
            "options": build_term_facet_options("ui_language", multi=True),
            "enabled": True,
        },
        "keywords": {
            "field": "keywords.keyword",
            "options": build_term_facet_options("keywords", multi=True),
            "enabled": True,
        },
        "origin": {
            "field": "origin.keyword",
            "options": build_term_facet_options("origin"),
            "enabled": True,
        },
        "audiences": {
            "field": "annotations.audiences.keyword",
            "options": build_term_facet_options("audiences", multi=True),
            "enabled": True,
        },
        "content_types": {
            "field": "annotations.content_types.keyword",
            "options": build_term_facet_options("content_types", multi=True),
            "enabled": True,
        },
        "tasks": {
            "field": "annotations.tasks.keyword",
            "options": build_term_facet_options("tasks", multi=True),
            "enabled": True,
        },
        "subject_domains": {
            "field": "annotations.subject_domains.keyword",
            "options": build_term_facet_options("subject_domains", multi=True),
            "enabled": True,
        },
    }


@extend_schema_view(
    retrieve=extend_schema(
        exclude=True,
    ),
    list=extend_schema(
        description=_("""Autocomplete for toollists."""),
        parameters=[query_param_q],
    ),
)
class AutoCompleteListDocumentViewSet(BaseDocumentViewSet):
    """ToolLists Auto-complete Search."""

    document = ListDocument
    document_uid_field = "id"
    serializer_class = AutoCompleteListDocumentSerializer
    pagination_class = None
    lookup_field = "id"
    filter_backends = [
        filter_backends.DefaultOrderingFilterBackend,
        CustomMultiMatchSearchFilterBackend,
    ]
    multi_match_search_fields = (
        "title",
        "title.gram2",
        "title.gram3",
        "description",
        "description.gram2",
        "description.gram3",
        "tools.name",
        "tools.name.gram2",
        "tools.name.gram3",
        "tools.title",
        "tools.title.gram2",
        "tools.title.gram3",
    )
    multi_match_options = {"type": "phrase_prefix"}

    ordering = "title.keyword"


@extend_schema_view(
    retrieve=extend_schema(
        exclude=True,
    ),
    list=extend_schema(
        description=_("""Full text search for toollists."""),
    ),
)
class ListDocumentViewSet(BaseDocumentViewSet):
    """ToolLists Full text search."""

    document = ListDocument
    document_uid_field = "id"
    serializer_class = ListDocumentSerializer
    pagination_class = Pagination
    filter_backends = [
        QueryStringFilterBackend,
        filter_backends.DefaultOrderingFilterBackend,
        filter_backends.OrderingFilterBackend,
    ]
    # Copy searchable fields list from document so we don't have two lists to
    # keep in sync between the index and this view.
    simple_query_string_search_fields = tuple(ListDocument.Django.fields)
    simple_query_string_options = {
        "analyze_wildcard": True,
        "lenient": True,
        "quote_field_suffix": ".exact",
    }

    ordering_fields = {
        "score": "_score",
        "title": "title.keyword",
        "created_date": "created_date",
        "modified_date": "modified_date",
    }
    ordering = ("_score", "-created_date", "title.keyword")
