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
from django.apps import apps
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
    content_type = serializers.CharField(
        source="content_type.model",
        read_only=True,
        default="",
        help_text=_("Content type of the revision."),
    )
    content_id = serializers.SerializerMethodField()
    parent_id = serializers.SerializerMethodField()
    child_id = serializers.SerializerMethodField()
    content_title = serializers.SerializerMethodField()

    def _should_hide_details(self, instance):
        """Should the details of this revision be hidden?"""
        user = self.context["request"].user
        return instance.revision.meta.suppressed and not (
            is_oversighter(user) or is_administrator(user)
        )

    def _get_revision_ids(self, instance):
        """Get a list of revision ids associated with the instance's model."""
        ctx_key = "revision_ids({}, {}, {})".format(
            instance.content_type.app_label,
            instance.content_type.model,
            instance.object_id,
        )
        if ctx_key in self.context:
            return self.context[ctx_key]

        target = apps.get_model(
            instance.content_type.app_label, instance.content_type.model
        ).objects.get(pk=instance.object_id)

        qs = Version.objects.get_for_object(target)
        qs = qs.order_by("id").values_list("id", flat=True)

        self.context[ctx_key] = list(qs)
        return self.context[ctx_key]

    def _get_parent_and_child_ids(self, instance):
        """Get the id of the previous and next versions."""
        ids = self._get_revision_ids(instance)

        current_idx = ids.index(instance.id)
        parent_idx = current_idx - 1
        parent_id = ids[parent_idx] if parent_idx >= 0 else None
        child_idx = current_idx + 1
        child_id = ids[child_idx] if child_idx < len(ids) else None

        return (parent_id, child_id)

    def to_representation(self, instance):
        """Generate primative representation of a model instance."""
        ret = super().to_representation(instance)
        if self._should_hide_details(instance):
            ret["user"] = {"id": -1, "username": _("username removed")}
            ret["comment"] = _("edit summary removed")
        return ret

    @extend_schema_field(schema.CONTENT_ID)
    def get_content_id(self, instance):
        """Get the identifier of the content being versioned"""
        if instance.content_type.model == "tool":
            return instance._local_field_dict["name"]
        elif instance.content_type.model == "toollist":
            return instance._local_field_dict["id"]

    @extend_schema_field(schema.VERSION_ID)
    def get_parent_id(self, instance):
        """Get the id of the previous version"""
        return self._get_parent_and_child_ids(instance)[0]

    @extend_schema_field(schema.VERSION_ID)
    def get_child_id(self, instance):
        """Get the id of the next version"""
        return self._get_parent_and_child_ids(instance)[1]

    @extend_schema_field(schema.CONTENT_TITLE)
    def get_content_title(self, instance):
        """Get the title of the content being versioned"""
        return instance._local_field_dict["title"]

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
            "content_type",
            "content_id",
            "parent_id",
            "child_id",
            "content_title",
        ]


@extend_schema_field(schema.JSONPATCH)
class JSONPatchField(serializers.JSONField):
    """JSONField with schema."""
