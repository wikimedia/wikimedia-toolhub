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
from .serializers import ToolDocumentSerializer


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
    pagination_class = pagination.QueryFriendlyPageNumberPagination
    document_uid_field = "name"
    lookup_field = "name"
    filter_backends = [
        filter_backends.CompoundSearchFilterBackend,
        filter_backends.DefaultOrderingFilterBackend,
        filter_backends.FacetedSearchFilterBackend,
        filter_backends.FilteringFilterBackend,
        filter_backends.OrderingFilterBackend,
    ]
    search_fields = (
        "name",
        "title",
        "description",
        "keywords",
        "subtitle",
        "url",
        "author",
        "repository",
        "url_alternates",
        "bot_username",
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
    )
    filter_fields = {
        "name": {
            "field": "name",
            "lookups": constants.STRING_LOOKUP_FILTERS,
        },
    }
    ordering_fields = {
        "name": "name.keyword",
        "title": "title",
        "created_date": "created_date",
    }
    ordering = ("_score", "-created_date", "name.keyword")
    faceted_search_fields = {
        "for_wikis": {
            "field": "for_wikis.keyword",
            "enabled": True,
        },
        "tool_type": {
            "field": "tool_type.keyword",
            "enabled": True,
        },
        "author": {
            "field": "author.keyword",
            "enabled": True,
        },
        "license": {
            "field": "license.keyword",
            "enabled": True,
        },
    }
