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

from rest_framework import serializers

from toolhub.apps.user.serializers import UserSerializer
from toolhub.decorators import doc
from toolhub.serializers import ModelSerializer

from .models import LogEntry


@doc(_("""Event action"""))  # noqa: W0223
class ActionField(serializers.ReadOnlyField):
    """Event action."""

    def to_representation(self, value):
        """Transform the *outgoing* native value into primitive data."""
        return LogEntry.ACTION_CHOICES[value][1]


@doc(_("""Event target"""))  # noqa: W0223
class TargetSerializer(serializers.Serializer):
    """Event target."""

    type = serializers.CharField(max_length=255, read_only=True)  # noqa: A003
    id = serializers.CharField(max_length=255, read_only=True)  # noqa: A003
    label = serializers.CharField(max_length=255, read_only=True)  # noqa: A003

    def to_representation(self, instance):
        """Convert a log entry target."""
        ret = {
            "type": instance.content_type.name,
            "id": instance.get_target_id(),
            "label": "",
        }

        try:
            ret["label"] = instance.get_target().auditlog_label
        except AttributeError:
            pass

        return ret


@doc(_("""Audit log entry"""))
class LogEntrySerializer(ModelSerializer):
    """Details of an audit log entry."""

    user = UserSerializer(many=False, read_only=True)
    action = ActionField()
    target = TargetSerializer(many=False, read_only=True, source="*")
    message = serializers.CharField(source="change_message", read_only=True)

    class Meta:
        """Configure serializer."""

        model = LogEntry
        fields = ["id", "timestamp", "user", "target", "action", "message"]
