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
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from toolhub.crawler.models import CrawledUrl

from ..permissions import IsAdminOrIsSelf
from ..permissions import IsCreator
from ..permissions import IsReadOnly
from ..serializers.crawler import CrawledUrlSerializer


class UrlViewSet(viewsets.ModelViewSet):
    """Manage URLs to crawl."""

    queryset = CrawledUrl.objects.all()
    serializer_class = CrawledUrlSerializer
    permission_classes = [IsCreator | IsReadOnly]
    filterset_fields = {
        "id": ["gt", "gte", "lt", "lte"],
        "created_by__username": ["exact", "contains", "startswith", "endswith"],
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

    @action(detail=False, permission_classes=[IsAdminOrIsSelf])
    def self(self, request):
        """Get URLs created by the current user."""
        qs = self.filter_queryset(
            CrawledUrl.objects.filter(created_by=request.user)
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
