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
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import permissions
from rest_framework import viewsets

from .models import ToolList
from .serializers import ToolListDetailSerializer
from .serializers import ToolListSerializer


@extend_schema_view(
    create=extend_schema(
        exclude=True,
    ),
    retrieve=extend_schema(
        description=_("""Details of a specific list of tools."""),
        responses=ToolListDetailSerializer,
    ),
    update=extend_schema(
        exclude=True,
    ),
    partial_update=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        exclude=True,
    ),
    list=extend_schema(
        description=_("""List all lists of tools."""),
    ),
)
class ToolListViewSet(viewsets.ModelViewSet):
    """ToolLists"""

    queryset = ToolList.objects.none()
    serializer_class = ToolListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = {
        "featured": ["exact"],
        "published": ["exact"],
    }
    ordering = ["-id"]

    def get_queryset(self):
        """Filter qs by current user when editing."""
        user = self.request.user
        if not user.is_authenticated:
            user = None
        qs = ToolList.objects.filter(favorites=False)
        if self.request.method not in permissions.SAFE_METHODS:
            return qs.filter(created_by=user)
        qs = qs.filter(Q(published=True) | Q(created_by=user))
        return qs

    def get_serializer_class(self):
        """Use different serializers for input vs output."""
        if self.action == "retrieve":
            return ToolListDetailSerializer
        return ToolListSerializer
