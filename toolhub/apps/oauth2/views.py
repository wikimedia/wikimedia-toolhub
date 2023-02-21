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
import urllib.parse

from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application
from oauth2_provider.views import AuthorizationView

from rest_framework import viewsets

from toolhub.permissions import ObjectPermissions
from toolhub.permissions import ObjectPermissionsOrAnonReadOnly

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
    permission_classes = [ObjectPermissionsOrAnonReadOnly]
    filterset_fields = {
        "user__username": ["exact"],
    }
    ordering = ["id"]

    def get_serializer_class(self):
        """Get the proper serializer for this request."""
        if self.request.method.upper() == "POST":
            return RegisterApplicationSerializer
        if self.request.method.upper() == "PATCH":
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

    queryset = AccessToken.objects.none()
    serializer_class = AuthorizationSerializer
    permission_classes = [ObjectPermissions]
    ordering = ["id"]

    def get_queryset(self):
        """Filter qs by current user."""
        return AccessToken.objects.filter(user=self.request.user)


class AuthzView(AuthorizationView):
    """Extend upstream AuthorizationView to override CSP values."""

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        resp = super().get(request, *args, **kwargs)

        try:
            # T329563: decorate the response with _csp_update
            # Add the configured redirect target as a form-action source.
            scopes, credentials = self.validate_authorization_request(request)
            uri, headers, body, status = self.create_authorization_response(
                request=self.request,
                scopes=" ".join(scopes),
                credentials=credentials,
                allow=True,
            )
            parsed_redirect = urllib.parse.urlparse(uri)
            resp._csp_update = {
                "form-action": "{}://{}".format(
                    parsed_redirect.scheme,
                    parsed_redirect.netloc,
                )
            }
        except OAuthToolkitError:
            # Should only happen if super().get(...) caught the same error
            return resp

        return resp
