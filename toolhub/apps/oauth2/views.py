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

from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application

from rest_framework import permissions
from rest_framework import viewsets

from toolhub.permissions import IsUser

from .serializers import ApplicationSerializer
from .serializers import AuthorizationSerializer
from .serializers import RegisterApplicationSerializer
from .serializers import UpdateApplicationSerializer


@extend_schema_view(
    list=extend_schema(
        description=_("""List all client applications."""),
    ),
    retrieve=extend_schema(
        description=_("""Info for a client application."""),
    ),
    create=extend_schema(
        description=_("""Register a new client application."""),
        responses=RegisterApplicationSerializer,
        request=RegisterApplicationSerializer,
    ),
    update=extend_schema(
        exclude=True,
    ),
    partial_update=extend_schema(
        description=_("""Update a client application."""),
        request=UpdateApplicationSerializer,
    ),
    destroy=extend_schema(
        description=_("""Delete a client application."""),
    ),
)
class ApplicationViewSet(viewsets.ModelViewSet):
    """Client applications."""

    queryset = Application.objects.all()
    lookup_field = "client_id"
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsUser,
    ]
    filterset_fields = {
        "user__username": ["exact"],
    }
    ordering = ["id"]

    def get_serializer_class(self):
        """Get the proper serializer for this request."""
        if self.request.method == "POST":
            return RegisterApplicationSerializer
        if self.request.method == "PATCH":
            return UpdateApplicationSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        """Create a new Application."""
        serializer.save(
            user=self.request.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            skip_authorization=False,
        )


@extend_schema_view(
    list=extend_schema(
        description=_("""List applications authorized by the current user."""),
    ),
    retrieve=extend_schema(
        description=_("""Info for an authorized application."""),
    ),
    create=extend_schema(
        exclude=True,
    ),
    update=extend_schema(
        exclude=True,
    ),
    partial_update=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        description=_("""Revoke an application authorization."""),
    ),
)
class AuthorizationViewSet(viewsets.ModelViewSet):
    """Client authorizations."""

    serializer_class = AuthorizationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsUser,
    ]
    ordering = ["id"]

    def get_queryset(self):
        """Filter qs by current user."""
        return AccessToken.objects.filter(user=self.request.user)
