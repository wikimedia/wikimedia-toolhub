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
import logging

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers

import reversion

from toolhub.apps.auditlog.context import auditlog_context
from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.toolinfo.serializers import SummaryToolSerializer
from toolhub.apps.user.models import ToolhubUser
from toolhub.apps.user.serializers import UserSerializer
from toolhub.apps.versioned.models import RevisionMetadata
from toolhub.apps.versioned.serializers import JSONPatchField
from toolhub.apps.versioned.serializers import RevisionSerializer
from toolhub.decorators import doc
from toolhub.serializers import EditCommentFieldMixin
from toolhub.serializers import ModelSerializer

from .models import ToolList
from .models import ToolListItem
from .validators import validate_favorites_unique
from .validators import validate_tools_exist
from .validators import validate_unique_list


logger = logging.getLogger(__name__)


@doc(_("""List of tools metadata."""))
class ToolListSerializer(ModelSerializer):
    """List of tools."""

    tools = serializers.SerializerMethodField()
    created_by = UserSerializer(many=False)
    modified_by = UserSerializer(many=False)

    class Meta:
        """Configure serializer."""

        model = ToolList
        fields = [
            "id",
            "title",
            "description",
            "icon",
            "favorites",
            "published",
            "featured",
            "tools",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ]
        read_only_fields = [
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ]

    @extend_schema_field(SummaryToolSerializer(many=True))
    def get_tools(self, obj):
        """Get ordered list of tools in toollist."""
        serializer = SummaryToolSerializer(
            obj.tools.all().order_by("toollistitem__order").distinct(),
            many=True,
        )
        return serializer.data


@doc(_("""Create or update a list."""))
class EditToolListSerializer(ModelSerializer, EditCommentFieldMixin):
    """Create or update a list."""

    tools = serializers.ListField(
        child=serializers.CharField(required=False),
        allow_empty=True,
        max_length=128,
        help_text=_("""List of tool names."""),
        validators=[
            validate_unique_list,
            validate_tools_exist,
        ],
    )

    class Meta:
        """Configure serializer."""

        model = ToolList
        fields = [
            "title",
            "description",
            "icon",
            "published",
            "tools",
            "comment",
        ]

    def to_representation(self, instance):
        """Proxy to ToolListSerializer for output."""
        serializer = ToolListSerializer(instance)
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        """Create a new tool list."""
        user = self.context["request"].user
        comment = validated_data.pop("comment", None)
        tools = validated_data.pop("tools", [])
        validated_data["tool_names"] = tools
        validated_data["created_by"] = user
        validated_data["modified_by"] = user

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(user)
            if comment is not None:
                reversion.set_comment(comment)

            with auditlog_context(user, comment):
                instance = ToolList.objects.create(**validated_data)
                for idx, name in enumerate(tools):
                    ToolListItem.objects.create(
                        toollist=instance,
                        tool=Tool.objects.get(name=name),
                        order=idx,
                        added_by=user,
                    )
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a tool list record."""
        user = self.context["request"].user
        comment = validated_data.pop("comment", None)
        tools = validated_data.pop("tools", [])

        # Compute changes to the list metadata
        instance_has_changes = False
        for key, value in validated_data.items():
            prior = getattr(instance, key)
            if value != prior:
                setattr(instance, key, value)
                instance_has_changes = True

        # Compute changes to the list contents
        list_qs = ToolListItem.objects.filter(toollist=instance)
        prior_tools = list(list_qs.values_list("tool__name", flat=True))
        # I thought about doing some really fancy list diffing here using
        # difflib.SequenceMatcher to find the minimal set of changes to the
        # list items so that the db update could be really targeted. After
        # playing with the idea it felt like a big pile of overkill, so
        # instead we will just compare the ordered lists and if anything is
        # different replace all of it below.
        list_has_changes = prior_tools != tools

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(user)
            if comment is not None:
                reversion.set_comment(comment)

            with auditlog_context(user, comment):
                if instance_has_changes:
                    instance.modified_by = user

                if list_has_changes:
                    # Save the list of tool names directly in our model as
                    # well as via the m2m relationship. This is a workaround
                    # for difficulties versioning m2m relations.
                    instance.tool_names = tools

                    # Delete prior list contents and then repopulate
                    list_qs.delete()
                    for idx, name in enumerate(tools):
                        ToolListItem.objects.create(
                            toollist=instance,
                            tool=Tool.objects.get(name=name),
                            order=idx,
                            added_by=user,
                        )

                if instance_has_changes or list_has_changes:
                    instance.save()
        return instance


@doc(_("""Historic revision of a list for generating diffs."""))
class ToolListDiffSerializer(ModelSerializer):
    """Historic revision of a list for generating diffs."""

    tools = serializers.ListField(
        child=serializers.CharField(required=False),
        allow_empty=True,
        max_length=128,
        help_text=_("""List of tool names."""),
        source="tool_names",
    )

    class Meta:
        """Configure serializer."""

        model = ToolList
        fields = [
            "id",
            "title",
            "description",
            "icon",
            "favorites",
            "published",
            "featured",
            "tools",
        ]
        read_only_fields = fields


@doc(_("""Historic revision of a list."""))
class ToolListHistoricVersionSerializer(ToolListDiffSerializer):
    """Historic revision of a list."""

    tools = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta(ToolListDiffSerializer.Meta):
        """Configure serializer."""

        fields = list(ToolListDiffSerializer.Meta.fields)
        fields.append("created_by")
        fields.append("created_date")
        read_only_fields = fields

    @extend_schema_field(SummaryToolSerializer(many=True))
    def get_tools(self, obj):
        """Get full tool objects"""
        serializer = SummaryToolSerializer(
            Tool.objects.filter(name__in=obj["tool_names"])
            .order_by("toollistitem__order")
            .distinct(),
            many=True,
        )
        return serializer.data

    @extend_schema_field(UserSerializer)
    def get_created_by(self, obj):
        """Get list creator object."""
        serializer = UserSerializer(
            ToolhubUser.objects.get(id=obj["created_by_id"])
        )
        return serializer.data


@doc(_("""Tool list revision."""))
class ToolListRevisionSerializer(RevisionSerializer):
    """Tool list revision."""

    class Meta(RevisionSerializer.Meta):
        """Configure serializer."""


@doc(_("""Tool list revision detail."""))
class ToolListRevisionDetailSerializer(ToolListRevisionSerializer):
    """Tool list revision."""

    toollist = ToolListHistoricVersionSerializer(
        source="field_dict", many=False
    )

    class Meta(ToolListRevisionSerializer.Meta):
        """Configure serializer."""

        fields = list(ToolListRevisionSerializer.Meta.fields)
        fields.append("toollist")

    def to_representation(self, instance):
        """Generate primative representation of a model instance."""
        ret = super().to_representation(instance)
        if self._should_hide_details(instance):
            ret["toollist"] = {}
        return ret


@doc(_("""Tool list revision difference."""))  # noqa: W0223
class ToolListRevisionDiffSerializer(serializers.Serializer):
    """Tool list revision difference."""

    original = ToolListRevisionSerializer(
        help_text=_("Revision to apply changes to."),
    )
    operations = JSONPatchField()
    result = ToolListRevisionSerializer(
        help_text=_("Revision after applying changes."),
    )


@doc(_("""Add a favorite tool."""))  # noqa: W0223
class AddFavoriteSerializer(serializers.Serializer):
    """Add a favorite tool."""

    name = serializers.CharField(
        help_text=_("""Tool name."""),
        validators=[
            validate_tools_exist,
            validate_favorites_unique,
        ],
    )

    def create(self, validated_data):
        """Create a new tool list."""
        name = validated_data.pop("name")
        validated_data["tool"] = Tool.objects.get(name=name)
        ToolListItem.objects.create(**validated_data)
        return validated_data["tool"]

    def to_representation(self, instance):
        """Proxy to SummaryToolSerializer for output."""
        serializer = SummaryToolSerializer(instance)
        return serializer.data
