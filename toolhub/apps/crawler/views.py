# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free oftware: you can redistribute it and/or modify
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

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from toolhub.permissions import IsAdminOrIsSelf
from toolhub.permissions import IsCreator
from toolhub.permissions import IsReadOnly

from .models import CrawledUrl
from .serializers import CrawledUrlSerializer
from .serializers import EditCrawledUrlSerializer


@extend_schema_view(
    create=extend_schema(
        description=_("""Register a new URL for crawling."""),
        request=EditCrawledUrlSerializer,
    ),
    retrieve=extend_schema(
        description=_("""Info for a specific crawled URL."""),
    ),
    update=extend_schema(
        description=_("""Update a specific URL."""),
        request=EditCrawledUrlSerializer,
    ),
    partial_update=extend_schema(
        description=_("""Update a specific URL."""),
        request=EditCrawledUrlSerializer,
    ),
    destroy=extend_schema(
        description=_("""Unregister an URL."""),
    ),
    list=extend_schema(  # noqa: A003
        description=_("""List all crawled URLs."""),
    ),
)
class UrlViewSet(viewsets.ModelViewSet):
    """Toolinfo URLs."""

    queryset = CrawledUrl.objects.all()
    serializer_class = CrawledUrlSerializer
    permission_classes = [IsCreator | IsReadOnly]
    filterset_fields = {
        "id": ["gt", "gte", "lt", "lte"],
        "created_by__username": [
            "exact",
            "contains",
            "startswith",
            "endswith",
        ],
        "url": ["contains"],
    }
    ordering_fields = ["id", "url"]
    ordering = ["id"]

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Set modified_by to current user."""
        serializer.save(modified_by=self.request.user)

    @extend_schema(
        description=_("""Get URLs created by the current user."""),
    )
    @action(detail=False, permission_classes=[IsAdminOrIsSelf])
    def self(self, request):
        """Owned item list."""
        qs = self.filter_queryset(
            CrawledUrl.objects.filter(created_by=request.user)
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
