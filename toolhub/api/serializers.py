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

from rest_framework import serializers

from social_django.models import UserSocialAuth

from toolhub.user.models import ToolhubUser


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

    def get_blocked(self, obj):
        """Get user's blocked status."""
        return self._from_extra_data(obj, "blocked", False)

    def get_registered(self, obj):
        """Get user's registration date."""
        return self._from_extra_data(obj, "registered")


class UserSerializer(serializers.ModelSerializer):
    """Describe API output for a User."""

    social_auth = UserSocialAuthSerializer(many=True, read_only=True)

    class Meta:
        """Configure serializer."""

        model = ToolhubUser
        fields = ["username", "groups", "date_joined", "social_auth"]
        read_only_fields = fields


class GroupSerializer(serializers.ModelSerializer):
    """Describe API output for a Group."""

    class Meta:
        """Configure serializer."""

        model = Group
        fields = ["name"]
        read_only_fields = fields
