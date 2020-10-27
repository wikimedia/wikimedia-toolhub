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
from django.contrib.auth.models import Group

from rest_framework import permissions
from rest_framework import viewsets

from toolhub.user.models import ToolhubUser

from ..serializers.user import GroupSerializer
from ..serializers.user import UserDetailSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """View user accounts registered with Toolhub."""

    queryset = ToolhubUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = {
        "id": ["gt", "gte", "lt", "lte"],
        "username": ["exact", "contains", "startswith", "endswith"],
        "date_joined": ["date__gt", "date__gte", "date__lt", "date__lte"],
    }
    ordering_fields = ["id", "username"]
    ordering = ["-date_joined"]


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """View user groups."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering_fields = ["id", "name"]
    ordering = ["id"]
