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

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from toolhub.decorators import doc
from toolhub.permissions import IsAdminOrIsSelf
from toolhub.permissions import IsCreator
from toolhub.permissions import IsReadOnly

from .models import CrawledUrl
from .serializers import CrawledUrlSerializer


@doc(_("""Manage URLs to crawl."""))
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

    @extend_schema(
        description=_("""Register a new URL for crawling."""),
    )
    def create(self, request, *args, **kwargs):
        """Create item."""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description=_("""Info for a specific crawled URL."""),
    )
    def retrieve(self, request, *args, **kwargs):
        """Item view."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description=_("""Update a specific URL."""),
    )
    def update(self, request, *args, **kwargs):
        """Put item."""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description=_("""Update a specific URL."""),
    )
    def partial_update(self, request, *args, **kwargs):
        """Patch item."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description=_("""Unregister an URL."""),
    )
    def destroy(self, request, *args, **kwargs):
        """Delete item."""
        # TODO: archive rather than delete?
        return super().destroy(request, *args, **kwargs)

    @extend_schema(  # noqa: A003
        description=_("""List all crawled URLs."""),
    )
    def list(self, request, *args, **kwargs):
        """List view."""
        return super().list(request, *args, **kwargs)
