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
import re

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from toolhub.apps.user.serializers import UserSerializer
from toolhub.decorators import doc
from toolhub.serializers import ModelSerializer

from .models import Tool


COMMONS_FILE_RE = re.compile(r"^https://commons.wikimedia.org/wiki/(File:.*)$")
COMMONS_FILE_TMPL = "https://commons.wikimedia.org/wiki/Special:FilePath/{}"


@doc(_("""A File: page on Commons"""))  # noqa: W0223
class CommonsFileOutputSerializer(serializers.Serializer):
    """A File: page on Commons."""

    page = serializers.CharField(
        max_length=2047, read_only=True, required=False
    )
    img = serializers.CharField(
        max_length=2047, read_only=True, required=False
    )

    def to_representation(self, instance):
        """Convert a commons File: url."""
        ret = {
            "page": instance,
            "img": None,
        }
        m = COMMONS_FILE_RE.match(instance)
        if m is not None:
            ret["img"] = COMMONS_FILE_TMPL.format(m[1])
        return ret


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


@doc(_("""Description of a tool"""))
class ToolSerializer(ModelSerializer):
    """Description of a tool."""

    for_wikis = ForWikiField(read_only=True, required=False)
    icon = CommonsFileOutputSerializer(
        many=False, read_only=True, required=False
    )
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
    """Create a tool"""

    def create(self, validated_data):
        """Create a new tool record."""
        comment = validated_data.pop("comment", None)
        obj, _, _ = Tool.objects.from_toolinfo(
            validated_data,
            self.context["request"].user,
            Tool.ORIGIN_API,
            comment,
        )
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
class UpdateToolSerializer(ModelSerializer, EditCommentFieldMixin):
    """Update a tool"""

    def update(self, instance, validated_data):
        """Update a tool record."""
        validated_data["name"] = instance.name
        comment = validated_data.pop("comment", None)
        obj, _, _ = Tool.objects.from_toolinfo(
            validated_data,
            self.context["request"].user,
            Tool.ORIGIN_API,
            comment,
        )
        return obj

    def to_representation(self, instance):
        """Proxy to ToolSerializer for output."""
        serializer = ToolSerializer(instance)
        return serializer.data

    class Meta:
        """Configure serializer."""

        model = Tool
        fields = [
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
