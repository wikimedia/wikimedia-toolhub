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
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers

from reversion.models import Version

from toolhub.apps.user.serializers import UserSerializer
from toolhub.permissions import is_administrator
from toolhub.permissions import is_oversighter
from toolhub.serializers import ModelSerializer

from . import schema


class RevisionSerializer(ModelSerializer):
    """Reusable serializer for revision summary information.

    Typical useage would be to import this serializer and then extend it for
    a particular type of versioned model such as a toolinfo record or a list
    of tools.
    """

    id = serializers.IntegerField(  # noqa: A003
        source="pk",
        help_text=_("A unique integer value identifying this revision."),
    )
    timestamp = serializers.DateTimeField(
        source="revision.date_created",
        read_only=True,
        help_text=("The timestamp of the revision."),
    )
    user = UserSerializer(source="revision.user", many=False, read_only=True)
    comment = serializers.CharField(
        source="revision.comment",
        read_only=True,
        default="",
        help_text=_("Comment by the user for the revision."),
    )
    suppressed = serializers.BooleanField(
        source="revision.meta.suppressed",
        read_only=True,
        default=False,
        help_text=_("Has this revision been marked as hidden?"),
    )
    patrolled = serializers.BooleanField(
        source="revision.meta.patrolled",
        read_only=True,
        default=False,
        help_text=_("Has this revision been reviewed by a patroller?"),
    )

    def _should_hide_details(self, instance):
        """Should the details of this revision be hidden?"""
        user = self.context["request"].user
        return instance.revision.meta.suppressed and not (
            is_oversighter(user) or is_administrator(user)
        )

    def to_representation(self, instance):
        """Generate primative representation of a model instance."""
        ret = super().to_representation(instance)
        if self._should_hide_details(instance):
            ret["user"] = {"id": -1, "username": _("username removed")}
            ret["comment"] = _("edit summary removed")
        return ret

    class Meta:
        """Configure serializer."""

        model = Version
        fields = [
            "id",
            "timestamp",
            "user",
            "comment",
            "suppressed",
            "patrolled",
        ]


@extend_schema_field(schema.JSONPATCH)
class JSONPatchField(serializers.JSONField):
    """JSONField with schema."""
