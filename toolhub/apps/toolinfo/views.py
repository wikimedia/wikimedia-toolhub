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
from .serializers import ToolSerializer


@extend_schema_view(
    list=extend_schema(
        description=_("""List all tools."""),
    ),
    retrieve=extend_schema(
        description=_("""Info for a specific tool."""),
    ),
)
class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    """Tools."""

    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = {
        "name": ["exact", "contains", "startswith", "endswith"],
    }
    ordering_fields = ["id", "name"]
    ordering = ["-modified_date"]
