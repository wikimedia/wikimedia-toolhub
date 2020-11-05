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

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers

from social_django.models import UserSocialAuth

from .models import ToolhubUser


class CurrentUserSerializer(serializers.Serializer):
    """Information about the current user."""

    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_anonymous = serializers.BooleanField(read_only=True)
    is_authenticated = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    csrf_token = serializers.CharField(read_only=True)

    def create(self, validated_data):
        """Operation not implemented."""
        raise NotImplementedError("Data output only serializer.")

    def upate(self, instance, validated_data):
        """Operation not implemented."""
        raise NotImplementedError("Data output only serializer.")


class UserSocialAuthSerializer(serializers.ModelSerializer):
    """Describe API output for a UserSocialAuth."""

    blocked = serializers.SerializerMethodField()
    registered = serializers.SerializerMethodField()

    class Meta:
        """Configure serializer."""

        model = UserSocialAuth
        fields = ["provider", "uid", "blocked", "registered"]
        read_only_fields = fields

    @classmethod
    def _from_extra_data(cls, obj, field, default=None):
        """Get a value from extra_data."""
        return obj.extra_data.get(field, default)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_blocked(self, obj):
        """Get user's blocked status."""
        return self._from_extra_data(obj, "blocked", False)

    @extend_schema_field(OpenApiTypes.INT)
    def get_registered(self, obj):
        """Get user's registration date."""
        return self._from_extra_data(obj, "registered")


class UserDetailSerializer(serializers.ModelSerializer):
    """Describe API output for a User."""

    social_auth = UserSocialAuthSerializer(many=True, read_only=True)

    class Meta:
        """Configure serializer."""

        model = ToolhubUser
        fields = ["id", "username", "groups", "date_joined", "social_auth"]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Describe API output for a User."""

    class Meta:
        """Configure serializer."""

        model = ToolhubUser
        fields = ["id", "username"]
        read_only_fields = fields


class GroupSerializer(serializers.ModelSerializer):
    """Describe API output for a Group."""

    class Meta:
        """Configure serializer."""

        model = Group
        fields = ["name"]
        read_only_fields = fields
