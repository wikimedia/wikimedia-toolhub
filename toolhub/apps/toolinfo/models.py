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
import logging

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from toolhub.apps.auditlog.context import auditlog_user
from toolhub.apps.auditlog.signals import registry
from toolhub.fields import JSONSchemaField

from . import schema


logger = logging.getLogger(__name__)


def name_to_slug(name):
    """Convert a tool name into a slug value."""
    return slugify(name, allow_unicode=True)


class ToolManager(models.Manager):
    """Custom manager for Tool models."""

    # 'oneOf' fields that will always be normalized as an array of values
    # when calling `from_toolinfo`.
    ARRAY_FIELDS = [
        "for_wikis",
        "sponsor",
        "available_ui_languages",
        "technology_used",
        "developer_docs_url",
        "user_docs_url",
        "feedback_url",
        "privacy_policy_url",
    ]

    # Fields allowed to change without considering the record to be "dirty"
    # and in need of persiting to the backing database when calling
    # `from_toolinfo`.
    VARIANT_FIELDS = ["created_by", "modified_by"]

    # Fields which are not allowed to change value once they have been set
    # initially.
    INVARIANT_FIELDS = ["origin"]

    def from_toolinfo(self, record, creator, origin):
        """Create or update a Tool using data from a toolinfo record.

        :param self: This manager
        :type self: ToolManager
        :param record: Toolinfo record. May be mutated as a side effect.
        :type record: dict
        :param creator: User creating/updating the record
        :type creator: settings.AUTH_USER_MODEL
        :param origin: Origin of this submission
        :type origin: str
        :returns: (tool (Tool), was_created (boolean), has_changes (boolean))
        :rtype: tuple
        """
        if record["name"].startswith("toolforge."):
            # Fixup tool names made by Striker to work as slugs
            record["name"] = "toolforge-" + record["name"][10:]
        record["name"] = name_to_slug(record["name"])

        record["created_by"] = creator
        record["modified_by"] = creator

        if "$schema" in record:
            record["_schema"] = record.pop("$schema")

        if "$language" in record:
            record["_language"] = record.pop("$language")

        record["origin"] = origin

        # Normalize 'oneOf' fields that could be an array of values or
        # a bare value to always be stored as an array of values.
        for field in self.ARRAY_FIELDS:
            if field in record and not isinstance(record[field], list):
                record[field] = [record[field]]

        if "keywords" in record:
            record["keywords"] = list(
                filter(
                    None, (s.strip() for s in record["keywords"].split(","))
                )
            )

        with auditlog_user(creator):
            tool, created = self.get_or_create(
                name=record["name"], defaults=record
            )
        if created:
            return tool, created, False

        # Compare input to prior model and decide if anything of note has
        # changed.
        has_changes = False

        for key, value in record.items():
            if key in self.VARIANT_FIELDS:
                continue

            prior = getattr(tool, key)

            if value != prior:
                if key in self.INVARIANT_FIELDS:
                    raise ValidationError(
                        _(
                            "Changing %(key)s after initial object creation "
                            "is not allowed"
                        ),
                        code="invariant",
                        params={"key": key},
                    )

                setattr(tool, key, value)
                has_changes = True
                logger.debug(
                    "%s: Updating %s to %s (was %s)",
                    record["name"],
                    key,
                    value,
                    prior,
                )
        if has_changes:
            with auditlog_user(creator):
                tool.save()

        # FIXME: what should we do if we get duplicates from
        # multiple source URLs? This can happen for example if
        # a Toolforge tool is registered independent of the
        # Striker managed toolinfo record.

        return tool, False, has_changes


@registry.register()
class Tool(models.Model):
    """Description of a tool."""

    TOOL_TYPE_CHOICES = (
        ("web app", _("web app")),
        ("desktop app", _("desktop app")),
        ("bot", _("bot")),
        ("gadget", _("gadget")),
        ("user script", _("user script")),
        ("command line tool", _("command line tool")),
        ("coding framework", _("coding framework")),
        ("other", _("other")),
    )

    ORIGIN_CRAWLER = "crawler"
    ORIGIN_API = "api"
    ORIGIN_CHOICES = (
        (ORIGIN_CRAWLER, _("crawler")),
        (ORIGIN_API, _("api")),
    )

    name = models.SlugField(
        unique=True,
        max_length=255,
        allow_unicode=True,
        help_text=_(
            "Unique identifier for this tool. Must be unique for every tool. "
            "It is recommended you prefix your tool names to reduce the risk "
            "of clashes."
        ),
    )
    title = models.CharField(
        max_length=255,
        help_text=_(
            "Human readable tool name. Recommended limit of 25 characters."
        ),
    )
    description = models.TextField(
        max_length=65535,
        help_text=_(
            "A longer description of the tool. "
            "The recommended length for a description is 3-5 sentences."
        ),
    )
    url = models.CharField(
        max_length=2047,
        help_text=_(
            "A direct link to the tool or to instructions on how to use or "
            "install the tool."
        ),
    )
    # TODO: Do we even want to persist this info? Valid per spec and stored in
    # db can be separate things.
    keywords = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        schema=schema.KEYWORDS,
    )
    author = models.CharField(
        blank=True,
        max_length=255,
        null=True,
        help_text=_("The primary tool developer."),
    )
    repository = models.CharField(
        blank=True,
        max_length=2047,
        null=True,
        help_text=_("A link to the repository where the tool code is hosted."),
    )
    subtitle = models.CharField(
        blank=True,
        max_length=255,
        null=True,
        help_text=_(
            "Longer than the full title but shorter than the description. "
            "It should add some additional context to the title."
        ),
    )
    openhub_id = models.CharField(
        blank=True,
        max_length=255,
        null=True,
        help_text=_(
            "The project ID on OpenHub. "
            "Given a URL of https://openhub.net/p/foo, "
            "the project ID is `foo`."
        ),
    )
    url_alternates = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_(
            "Alternate links to the tool or install documentation in "
            "different natural languages."
        ),
        schema=schema.schema_for("url_alternates"),
    )
    bot_username = models.CharField(
        blank=True,
        max_length=255,
        null=True,
        help_text=_(
            "If the tool is a bot, the Wikimedia username of the bot. "
            "Do not include 'User:' or similar prefixes."
        ),
    )
    deprecated = models.BooleanField(
        default=False,
        help_text=_(
            "If true, the use of this tool is officially discouraged. "
            "The `replaced_by` parameter can be used to define a replacement."
        ),
    )
    replaced_by = models.TextField(
        blank=True,
        max_length=2047,
        null=True,
        help_text=_(
            "If this tool is deprecated, this parameter should be used to "
            "link to the replacement tool."
        ),
    )
    experimental = models.BooleanField(
        default=False,
        help_text=_(
            "If true, this tool is unstable and can change or "
            "go offline at any time."
        ),
    )
    for_wikis = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_(
            "A string or array of strings describing the wiki(s) this tool "
            "can be used on. Use hostnames such as `zh.wiktionary.org`. Use "
            "asterisks as wildcards. For example, `*.wikisource.org` means "
            "'this tool works on all Wikisource wikis.' `*` means "
            "'this works on all wikis, including Wikimedia wikis.'"
        ),
        schema=schema.schema_for("for_wikis", oneof=0),
    )
    icon = models.CharField(
        blank=True,
        max_length=2047,
        null=True,
        validators=[
            validators.RegexValidator(
                regex=r"^https://commons.wikimedia.org/wiki/File:.+\\..+$"
            ),
        ],
        help_text=_(
            "A link to a Wikimedia Commons file description page for an icon "
            "that depicts the tool."
        ),
    )
    # TODO: pick list/validation of SPDX identifiers
    license = models.CharField(  # noqa: A003
        blank=True,
        max_length=255,
        null=True,
        help_text=_(
            "The software license the tool code is available under. "
            "Use a standard SPDX license identifier like 'GPL-3.0-or-later'."
        ),
    )
    sponsor = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_("Organization(s) that sponsored the tool's development."),
        schema=schema.schema_for("sponsor", oneof=1),
    )
    available_ui_languages = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_(
            "The language(s) the tool's interface has been translated into. "
            "Use ISO 639 language codes like `zh` and `scn`. If not defined "
            "it is assumed the tool is only available in English."
        ),
        schema=schema.schema_for("available_ui_languages", oneof=0),
    )
    technology_used = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_(
            "A string or array of strings listing technologies "
            "(programming languages, development frameworks, etc.) used in "
            "creating the tool."
        ),
        schema=schema.schema_for("technology_used", oneof=1),
    )
    tool_type = models.CharField(
        choices=TOOL_TYPE_CHOICES,
        blank=True,
        max_length=32,
        null=True,
        help_text=_(
            "The manner in which the tool is used. "
            "Select one from the list of options."
        ),
    )
    api_url = models.TextField(
        blank=True,
        max_length=2047,
        null=True,
        help_text=_("A link to the tool's API, if available."),
    )
    developer_docs_url = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_(
            "A link to the tool's developer documentation, if available."
        ),
        schema=schema.schema_for("developer_docs_url", oneof=0),
    )
    user_docs_url = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_("A link to the tool's user documentation, if available."),
        schema=schema.schema_for("user_docs_url", oneof=0),
    )
    feedback_url = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_(
            "A link to location where the tool's user can leave feedback."
        ),
        schema=schema.schema_for("feedback_url", oneof=0),
    )
    privacy_policy_url = JSONSchemaField(
        blank=True,
        default=list,
        null=True,
        help_text=_("A link to the tool's privacy policy, if available."),
        schema=schema.schema_for("privacy_policy_url", oneof=0),
    )
    translate_url = models.TextField(
        blank=True,
        max_length=2047,
        null=True,
        help_text=_("A link to the tool's translation interface."),
    )
    bugtracker_url = models.TextField(
        blank=True,
        max_length=2047,
        null=True,
        help_text=_(
            "A link to the tool's bug tracker on GitHub, Bitbucket, "
            "Phabricator, etc."
        ),
    )
    _schema = models.CharField(
        blank=True,
        max_length=32,
        null=True,
        help_text=_(
            "A URI identifying the jsonschema for this toolinfo.json record. "
            "This should be a short uri containing only the name and revision "
            "at the end of the URI path."
        ),
    )
    _language = models.CharField(
        blank=True,
        max_length=16,
        null=True,
        validators=[
            validators.RegexValidator(regex=r"^(x-.*|[A-Za-z]{2,3}(-.*)?)$")
        ],
        help_text=_(
            "The language in which this toolinfo record is written. "
            "If not set, the default value is English. "
            "Use ISO 639 language codes."
        ),
    )

    origin = models.CharField(
        choices=ORIGIN_CHOICES,
        max_length=32,
        default=ORIGIN_CRAWLER,
        help_text=_("Origin of this tool record."),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tools",
        db_index=True,
        on_delete=models.CASCADE,
    )
    created_date = models.DateTimeField(
        default=timezone.now, blank=True, editable=False, db_index=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(
        default=timezone.now, blank=True, editable=False, db_index=True
    )

    objects = ToolManager()

    @property
    def auditlog_label(self):
        """Get label for use in auditlog output."""
        return self.name
