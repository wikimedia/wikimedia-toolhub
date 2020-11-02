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
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema

from rest_framework import permissions
from rest_framework import viewsets

from toolhub.apps.user.models import ToolhubUser

from ..decorators import doc
from ..serializers.user import GroupSerializer
from ..serializers.user import UserDetailSerializer


@doc(_("""View users."""))
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Toolhub users."""

    queryset = ToolhubUser.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = {
        "id": ["gt", "gte", "lt", "lte"],
        "username": ["exact", "contains", "startswith", "endswith"],
        "date_joined": ["date__gt", "date__gte", "date__lt", "date__lte"],
    }
    ordering_fields = ["id", "username"]
    ordering = ["-date_joined"]

    @extend_schema(  # noqa: A003
        description=_("""List all active users."""),
    )
    def list(self, request, *args, **kwargs):
        """List view."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=_("""Info for a specific user."""),
    )
    def retrieve(self, request, *args, **kwargs):
        """Item view."""
        return super().retrieve(request, *args, **kwargs)


@doc(_("""View user groups."""))
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Django user groups."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    ordering_fields = ["id", "name"]
    ordering = ["id"]

    @extend_schema(  # noqa: A003
        description=_("""List all user groups."""),
    )
    def list(self, request, *args, **kwargs):
        """List view."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=_("""Info for a user group."""),
    )
    def retrieve(self, request, *args, **kwargs):
        """Item view."""
        return super().retrieve(request, *args, **kwargs)
