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
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

import reversion

from toolhub.apps.auditlog.context import auditlog_context
from toolhub.apps.user.serializers import UserSerializer
from toolhub.apps.versioned.models import RevisionMetadata
from toolhub.apps.versioned.serializers import JSONPatchField
from toolhub.apps.versioned.serializers import RevisionSerializer
from toolhub.decorators import doc
from toolhub.serializers import EditCommentFieldMixin
from toolhub.serializers import ModelSerializer

from .models import Annotations
from .models import Tool


@doc(_("""SPDX license information"""))  # noqa: W0223
class SpdxLicenseSerializer(serializers.Serializer):
    """SPDX license information."""

    id = serializers.CharField(  # noqa: A003
        source="licenseId",
        max_length=255,
        read_only=True,
        help_text=_("SPDX license ID"),
    )
    name = serializers.CharField(
        max_length=255,
        read_only=True,
        help_text=_("Full name of this license"),
    )
    osi_approved = serializers.BooleanField(
        source="isOsiApproved",
        read_only=True,
        help_text=_("Is this license approved as 'open source' by the OSI?"),
    )
    fsf_approved = serializers.BooleanField(
        source="isFsfLibre",
        read_only=True,
        help_text=_("Is this license approved as 'free software' by the FSF?"),
    )
    deprecated = serializers.BooleanField(
        source="isDeprecatedLicenseId",
        read_only=True,
        help_text=_("Is this license considered to be outdated?"),
    )


@doc(_("Community added information for a tool"))
class AnnotationsSerializer(ModelSerializer):
    """Community added information for a tool."""

    class Meta:
        """Configure serializer."""

        model = Annotations
        fields = [
            "wikidata_qid",
            # Fields from CommonFieldsMixin
            "deprecated",
            "replaced_by",
            "experimental",
            "for_wikis",
            "icon",
            "available_ui_languages",
            "tool_type",
            "api_url",
            "developer_docs_url",
            "user_docs_url",
            "feedback_url",
            "privacy_policy_url",
            "translate_url",
            "bugtracker_url",
        ]


@doc(_("""Update annotations"""))
class UpdateAnnotationsSerializer(ModelSerializer, EditCommentFieldMixin):
    """Update a tool's annotations"""

    class Meta:
        """Configure serializer."""

        model = Annotations
        fields = list(AnnotationsSerializer.Meta.fields)
        fields.append("comment")

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an annotations record."""
        user = self.context["request"].user
        comment = validated_data.pop("comment", None)

        has_changes = False
        for key, value in validated_data.items():
            prior = getattr(instance, key)
            if value != prior:
                setattr(instance, key, value)
                has_changes = True

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(user)
            if comment is not None:
                reversion.set_comment(comment)

            with auditlog_context(user, comment):
                if has_changes:
                    instance.save()
                    instance.tool.modified_by = user
                    instance.tool.save()
        return instance

    def to_representation(self, instance):
        """Proxy to AnnotationsSerializer for output."""
        serializer = AnnotationsSerializer(instance)
        return serializer.data


@doc(_("""Description of a tool"""))
class ToolSerializer(ModelSerializer):
    """Description of a tool."""

    annotations = AnnotationsSerializer(many=False, read_only=True)
    created_by = UserSerializer(many=False, read_only=True)
    modified_by = UserSerializer(many=False, read_only=True)

    class Meta:
        """Configure serializer."""

        model = Tool
        fields = [
            "name",
            "title",
            "description",
            "url",
            "keywords",
            "author",
            "repository",
            "subtitle",
            "openhub_id",
            "url_alternates",
            "bot_username",
            "deprecated",
            "replaced_by",
            "experimental",
            "for_wikis",
            "icon",
            "license",
            "sponsor",
            "available_ui_languages",
            "technology_used",
            "tool_type",
            "api_url",
            "developer_docs_url",
            "user_docs_url",
            "feedback_url",
            "privacy_policy_url",
            "translate_url",
            "bugtracker_url",
            "annotations",
            "_schema",
            "_language",
            "origin",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ]


@doc(_("""Summary of a tool"""))
class SummaryToolSerializer(ModelSerializer):
    """Summary of a tool."""

    class Meta:
        """Configure serializer."""

        model = Tool
        fields = [
            "name",
            "title",
            "description",
            "url",
            "keywords",
            "author",
            "icon",
        ]
        read_only_fields = fields


@doc(_("""Create a tool"""))
class CreateToolSerializer(ModelSerializer, EditCommentFieldMixin):
    """Create a tool."""

    def create(self, validated_data):
        """Create a new tool record."""
        comment = validated_data.pop("comment", None)
        try:
            obj, _, _ = Tool.objects.from_toolinfo(
                validated_data,
                self.context["request"].user,
                Tool.ORIGIN_API,
                comment,
            )
        except ValidationError as e:
            raise PermissionDenied(e.messages[0], e.code) from e
        return obj

    def to_representation(self, instance):
        """Proxy to ToolSerializer for output."""
        serializer = ToolSerializer(instance)
        return serializer.data

    def to_internal_value(self, data):
        """Transform the incoming primitive data to a native value."""
        data = super().to_internal_value(data)
        return Tool.objects.normalize_toolinfo(data)

    class Meta:
        """Configure serializer."""

        model = Tool
        fields = [
            "name",
            "title",
            "description",
            "url",
            "keywords",
            "author",
            "repository",
            "subtitle",
            "openhub_id",
            "url_alternates",
            "bot_username",
            "deprecated",
            "replaced_by",
            "experimental",
            "for_wikis",
            "icon",
            "license",
            "sponsor",
            "available_ui_languages",
            "technology_used",
            "tool_type",
            "api_url",
            "developer_docs_url",
            "user_docs_url",
            "feedback_url",
            "privacy_policy_url",
            "translate_url",
            "bugtracker_url",
            "_language",
            "comment",
        ]


@doc(_("""Update a tool"""))
class UpdateToolSerializer(CreateToolSerializer):
    """Update a tool"""

    def update(self, instance, validated_data):
        """Update a tool record."""
        validated_data["name"] = instance.name
        comment = validated_data.pop("comment", None)
        try:
            obj, _, _ = Tool.objects.from_toolinfo(
                validated_data,
                self.context["request"].user,
                instance.origin,
                comment,
            )
        except ValidationError as e:
            raise PermissionDenied(e.messages[0], e.code) from e
        return obj

    def to_internal_value(self, data):
        """Transform the incoming primitive data to a native value."""
        data = super().to_internal_value(data)
        return Tool.objects.normalize_toolinfo(data)

    class Meta(CreateToolSerializer.Meta):
        """Configure serializer."""

        # Remove "name" from parent's fields list
        fields = CreateToolSerializer.Meta.fields[1:]


@doc(_("""Tool revision."""))
class ToolRevisionSerializer(RevisionSerializer):
    """Tool revision."""

    class Meta(RevisionSerializer.Meta):
        """Configure serializer."""


@doc(_("""Tool revision detail."""))
class ToolRevisionDetailSerializer(ToolRevisionSerializer):
    """Tool revision details."""

    toolinfo = serializers.SerializerMethodField()

    def to_representation(self, instance):
        """Generate primative representation of a model instance."""
        ret = super().to_representation(instance)
        if self._should_hide_details(instance):
            ret["toolinfo"] = {}
        return ret

    def _get_historic_data(self, obj):
        """Get historic data for a given Tool version."""
        data = obj.field_dict

        data["annotations"] = {}
        qs = obj.revision.version_set.get_for_model(Annotations)
        ann = qs.first()
        if ann is not None:
            data["annotations"] = ann.field_dict

        return data

    @extend_schema_field(ToolSerializer(many=False))
    def get_toolinfo(self, obj):
        """Get historic toolinfo."""
        serializer = ToolSerializer(self._get_historic_data(obj), many=False)
        return serializer.data

    class Meta(ToolRevisionSerializer.Meta):
        """Configure serializer."""

        fields = list(ToolRevisionSerializer.Meta.fields)
        fields.append("toolinfo")


@doc(_("""Tool revision difference."""))  # noqa: W0223
class ToolRevisionDiffSerializer(serializers.Serializer):
    """Tool revision difference."""

    original = ToolRevisionSerializer(
        help_text=_("Revision to apply changes to."),
    )
    operations = JSONPatchField()
    result = ToolRevisionSerializer(
        help_text=_("Revision after applying changes."),
    )
