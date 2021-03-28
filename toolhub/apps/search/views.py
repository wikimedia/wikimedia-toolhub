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

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from .documents import ToolDocument
from .schema import FACET_RESPONSE
from .serializers import ToolDocumentSerializer


class QueryStringFilterBackend(  # noqa: W0223
    filter_backends.BaseSearchFilterBackend
):
    """Custom search filter backend."""

    matching = constants.MATCHING_OPTION_MUST
    query_backends = [
        filter_backends.search.query_backends.SimpleQueryStringQueryBackend,
    ]


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
        description=_("""Faceted search for tools."""),
    ),
)
class ToolDocumentViewSet(BaseDocumentViewSet):
    """Full text search."""

    document = ToolDocument
    serializer_class = ToolDocumentSerializer
    pagination_class = Pagination
    document_uid_field = "name"
    lookup_field = "name"
    filter_backends = [
        QueryStringFilterBackend,
        filter_backends.DefaultOrderingFilterBackend,
        filter_backends.FacetedSearchFilterBackend,
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
    ]
    simple_query_string_search_fields = ()
    simple_query_string_options = {
        "lenient": True,
        "quote_field_suffix": ".exact",
        "all_fields": True,
    }
    filter_fields = {
        "name": {
            "field": "name",
            "lookups": constants.STRING_LOOKUP_FILTERS,
        },
        "wiki": {
            "field": "for_wikis.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
        "tool_type": {
            "field": "tool_type.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
        "author": {
            "field": "author.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
        "license": {
            "field": "license.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
        "ui_language": {
            "field": "available_ui_languages.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
        "keywords": {
            "field": "keywords.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
        "origin": {
            "field": "origin.keyword",
            "lookups": [
                constants.LOOKUP_FILTER_TERM,
                constants.LOOKUP_QUERY_ISNULL,
            ],
        },
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
            "field": "for_wikis.keyword",
            "options": build_term_facet_options("wiki", multi=True),
            "enabled": True,
        },
        "tool_type": {
            "field": "tool_type.keyword",
            "options": build_term_facet_options("tool_type"),
            "enabled": True,
        },
        "author": {
            "field": "author.keyword",
            "options": build_term_facet_options("author"),
            "enabled": True,
        },
        "license": {
            "field": "license.keyword",
            "options": build_term_facet_options("license"),
            "enabled": True,
        },
        "ui_language": {
            "field": "available_ui_languages.keyword",
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
    }
