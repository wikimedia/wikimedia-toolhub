# Copyright (c) 2021 Wikimedia Foundation and contributors.
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
from django.contrib.auth.models import Group
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from reversion.models import Version

from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.user.serializers import UserSerializer
from toolhub.decorators import doc
from toolhub.serializers import JSONSchemaField
from toolhub.serializers import ModelSerializer

from .models import LogEntry


@doc(_("""Event action"""))  # noqa: W0223
class ActionField(serializers.ReadOnlyField):
    """Event action."""

    def to_representation(self, value):
        """Transform the *outgoing* native value into primitive data."""
        with translation.override("en"):
            try:
                return str(LogEntry.ACTION_CHOICES[value][1])
            except IndexError:
                # Should only happen in development environments when log
                # events have been placed in the db using code that is not
                # merged yet.
                return value


@doc(_("""Event target"""))  # noqa: W0223
class TargetSerializer(serializers.Serializer):
    """Event target."""

    type = serializers.CharField(max_length=255, read_only=True)  # noqa: A003
    id = serializers.CharField(max_length=255, read_only=True)  # noqa: A003
    label = serializers.CharField(max_length=255, read_only=True)  # noqa: A003

    def to_representation(self, instance):
        """Convert a log entry target."""
        with translation.override("en"):
            ret = {
                "type": str(instance.content_type.name),
                "id": instance.get_target_id(),
                "label": "",
            }

        target = instance.get_target()
        try:
            ret["label"] = target.auditlog_label
            if isinstance(target, Tool):
                # T274020: Replace Tool id with name for API usage
                ret["id"] = target.auditlog_label
        except AttributeError:
            pass

        if isinstance(target, Group):
            ret["label"] = target.name

        return ret


@doc(_("""Event parameters"""))  # noqa: W0223
class ParamsField(JSONSchemaField):
    """Event parameters."""

    def to_representation(self, obj):
        """Transform the *outgoing* native value into primitive data."""
        raw = super().to_representation(obj)
        if raw.get("revision"):
            # When we have a revision, add its meta data to the output.
            meta = (
                Version.objects.select_related("revision", "revision__meta")
                .get(pk=raw["revision"])
                .revision.meta
            )
            raw["suppressed"] = meta.suppressed
            raw["patrolled"] = meta.patrolled
        return raw


@doc(_("""Audit log entry"""))
class LogEntrySerializer(ModelSerializer):
    """Details of an audit log entry."""

    user = UserSerializer(many=False, read_only=True)
    target = TargetSerializer(many=False, read_only=True, source="*")
    action = ActionField()
    message = serializers.CharField(source="change_message", read_only=True)

    def build_standard_field(self, field_name, model_field):
        """Create regular model fields."""
        cls, args = super().build_standard_field(field_name, model_field)
        if field_name == "params":
            # Hacky way to override the class for our params collection
            cls = ParamsField
        return cls, args

    class Meta:
        """Configure serializer."""

        model = LogEntry
        fields = [
            "id",
            "timestamp",
            "user",
            "target",
            "action",
            "params",
            "message",
        ]
