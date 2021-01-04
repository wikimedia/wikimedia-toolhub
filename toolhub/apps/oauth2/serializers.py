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

from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application

from rest_framework import serializers

from toolhub.apps.user.serializers import UserSerializer
from toolhub.decorators import doc
from toolhub.serializers import ModelSerializer


@doc(_("""OAuth Client application."""))
class ApplicationSerializer(ModelSerializer):
    """An OAuth Client application."""

    name = serializers.CharField(
        max_length=255,
        allow_blank=False,
        label=_("Application name"),
        help_text=_("Something users will recognize and trust"),
    )
    redirect_url = serializers.URLField(
        max_length=255,
        source="redirect_uris",
        label=_("Authorization callback URL"),
        help_text=_("The application's callback URL."),
    )
    client_id = serializers.CharField(
        max_length=100,
        read_only=True,
        help_text=_("Public identifier for this application"),
    )
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        """Configure serializer."""

        model = Application
        fields = [
            "name",
            "redirect_url",
            "client_id",
            "user",
        ]
        read_only_fields = fields


@doc(_("""OAuth Client application registration."""))
class RegisterApplicationSerializer(ApplicationSerializer):
    """An OAuth Client application registration."""

    client_secret = serializers.CharField(
        max_length=255,
        read_only=True,
        help_text=_(
            "Secret known only to the application and the authorization server"
        ),
    )

    class Meta:
        """Configure serializer."""

        model = Application
        fields = [
            "name",
            "redirect_url",
            "client_id",
            "client_secret",
            "user",
        ]
        read_only_fields = ["client_id", "client_secret"]


@doc(_("""OAuth Client application update."""))
class UpdateApplicationSerializer(ModelSerializer):
    """An OAuth Client application update."""

    redirect_url = serializers.URLField(
        max_length=255,
        source="redirect_uris",
        label=_("Authorization callback URL"),
        help_text=_("The application's callback URL."),
    )

    def to_representation(self, instance):
        """Proxy to ApplicationSerializer for output."""
        serializer = ApplicationSerializer(instance)
        return serializer.data

    class Meta:
        """Configure serializer."""

        model = Application
        fields = [
            "redirect_url",
        ]


@doc(_("""Authorized OAuth client application."""))
class AuthorizationSerializer(ModelSerializer):
    """Authorized OAuth client application."""

    user = UserSerializer(many=False, read_only=True)
    application = ApplicationSerializer(many=False, read_only=True)

    class Meta:
        """Configure serializer."""

        model = AccessToken
        fields = ["id", "user", "application", "created", "updated", "expires"]
        read_only_fields = fields
