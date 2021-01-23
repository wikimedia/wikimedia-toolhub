# Copyright (c) 2020 Wikimedia Foundation and contributors.
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

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import permissions
from rest_framework import viewsets

from .models import Tool
from .serializers import CreateToolSerializer
from .serializers import ToolSerializer
from .serializers import UpdateToolSerializer


@extend_schema_view(
    create=extend_schema(
        description=_("""Create a new tool."""),
        request=CreateToolSerializer,
        responses=ToolSerializer,
    ),
    retrieve=extend_schema(
        description=_("""Info for a specific tool."""),
    ),
    update=extend_schema(
        description=_("""Update info for a specific tool."""),
        request=UpdateToolSerializer,
        responses=ToolSerializer,
    ),
    partial_update=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        description=_("""Delete a tool."""),
    ),
    list=extend_schema(
        description=_("""List all tools."""),
    ),
)
class ToolViewSet(viewsets.ModelViewSet):
    """Tools."""

    lookup_field = "name"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = {
        "name": ["exact", "contains", "startswith", "endswith"],
    }
    ordering_fields = ["name", "modified_date"]
    ordering = ["-modified_date"]

    def get_queryset(self):
        """Filter qs by current user when editing."""
        if self.request.method in ["DELETE", "PUT"]:
            return Tool.objects.filter(created_by=self.request.user)
        return Tool.objects.all()

    def get_serializer_class(self):
        """Use different serializers for input vs output."""
        if self.request.method == "POST":
            return CreateToolSerializer
        if self.request.method == "PUT":
            return UpdateToolSerializer
        return ToolSerializer
