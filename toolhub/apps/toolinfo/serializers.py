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
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from reversion.models import Version

from toolhub.apps.user.serializers import UserSerializer
from toolhub.decorators import doc
from toolhub.serializers import ModelSerializer

from . import schema
from .models import Tool


@doc(_("""Supported wikis"""))  # noqa: W0223
class ForWikiField(serializers.JSONField):
    """Supported wikis."""

    TRANSLATIONS = {
        "*": _("Any wiki"),
        "commons.wikimedia.org": _("Wikimedia Commons"),
        "mediawiki.org": _("MediaWiki wiki"),
        "species.wikimedia.org": _("Wikispecies"),
        "wikibooks.org": _("Any Wikibooks"),
        "wikidata.org": _("Wikidata"),
        "wikinews.org": _("Any Wikinews"),
        "wikipedia.org": _("Any Wikipedia"),
        "wikiquote.org": _("Any Wikiquote"),
        "wikisource.org": _("Any Wikisource"),
        "wikiversity.org": _("Any Wikiversity"),
        "wikivoyage.org": _("Any Wikivoyage"),
        "wiktionary.org": _("Any Wiktionary"),
    }

    def _localize_label(self, label):
        """Localize a wiki label."""
        parts = label.split(".")
        if len(parts) == 3 and parts[0] in ["*", "www"]:
            # Strip off "*." and "www." prefix before lookup
            label = ".".join(parts[1:])

        return self.TRANSLATIONS.get(label, label)

    def to_representation(self, value):
        """Convert a list of wikis."""
        return [self._localize_label(v) for v in value]


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


@doc(_("""Description of a tool"""))
class ToolSerializer(ModelSerializer):
    """Description of a tool."""

    for_wikis = ForWikiField(read_only=True, required=False)
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
            "_schema",
            "_language",
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
        fields = ["name", "title", "url"]
        read_only_fields = fields


class EditCommentFieldMixin(metaclass=serializers.SerializerMetaclass):
    """Reversion comment.

    When using you must add "comment" to the meta.fields collection manually.
    """

    comment = serializers.CharField(
        label=_("""Edit summary"""),
        help_text=_(
            """Description of the changes you are making """
            """to this toolinfo record."""
        ),
        write_only=True,
        required=False,
    )

    def get_comment(self, instance):  # noqa: W0613
        """Placeholder method needed for comment field."""
        return ""


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
                Tool.ORIGIN_API,
                comment,
            )
        except ValidationError as e:
            raise PermissionDenied(e.messages[0], e.code) from e
        return obj

    class Meta(CreateToolSerializer.Meta):
        """Configure serializer."""

        # Remove "name" from parent's fields list
        fields = CreateToolSerializer.Meta.fields[1:]


@doc(_("""Tool revision."""))
class ToolRevisionSerializer(ModelSerializer):
    """Tool revision."""

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

    class Meta:
        """Configure serializer."""

        model = Version
        fields = ["id", "timestamp", "user", "comment"]


@doc(_("""Tool revision detail."""))
class ToolRevisionDetailSerializer(ToolRevisionSerializer):
    """Tool revision details."""

    toolinfo = ToolSerializer(source="field_dict", many=False)

    class Meta(ToolRevisionSerializer.Meta):
        """Configure serializer."""

        fields = list(ToolRevisionSerializer.Meta.fields)
        fields.append("toolinfo")


@extend_schema_field(schema.JSONPATCH)
class JSONPatchField(serializers.JSONField):
    """JSONField with schema."""


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
