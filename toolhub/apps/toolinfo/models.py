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
import functools
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from django_prometheus.models import ExportModelOperationsMixin

import reversion
from reversion.signals import post_revision_commit

from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel

from toolhub.apps.auditlog.context import auditlog_context
from toolhub.apps.auditlog.models import LogEntry
from toolhub.apps.auditlog.signals import registry
from toolhub.apps.versioned.models import RevisionMetadata
from toolhub.fields import BlankAsNullCharField
from toolhub.fields import BlankAsNullTextField
from toolhub.fields import JSONSchemaField

from . import schema
from .utils import language_data
from .validators import validate_language_code
from .validators import validate_language_code_list
from .validators import validate_spdx
from .validators import validate_url_mutilingual_list


logger = logging.getLogger(__name__)


def name_to_slug(name):
    """Convert a tool name into a slug value."""
    return slugify(name, allow_unicode=True)


class ToolManager(SafeDeleteManager):
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

    URL_MULTILINGUAL_FIELDS = [
        "developer_docs_url",
        "user_docs_url",
        "feedback_url",
        "privacy_policy_url",
        "url_alternates",
    ]

    # Fields allowed to change without considering the record to be "dirty"
    # and in need of persiting to the backing database when calling
    # `from_toolinfo`.
    VARIANT_FIELDS = ["created_by", "modified_by"]

    # Fields which are not allowed to change value once they have been set
    # initially.
    INVARIANT_FIELDS = ["origin"]

    # Extra fields that we allow to pass through normalize_toolinfo
    EXTRA_ALLOWED_FIELDS = ["comment"]

    # Lazily populated list of all field names.
    ALL_FIELDS = None

    DEFAULT_LANGUAGE = "en"

    def _valid_field_names(self):
        """List of all valid Tool model field names."""
        if self.ALL_FIELDS is None:
            self.ALL_FIELDS = [field.name for field in Tool._meta.fields]
        return self.ALL_FIELDS

    def normalize_toolinfo(self, record):
        """Normalize incoming record formatting."""
        if "name" in record:
            if record["name"].startswith("toolforge."):
                # Fixup tool names made by Striker to work as slugs
                record["name"] = "toolforge-" + record["name"][10:]
            record["name"] = name_to_slug(record["name"])

        if "$schema" in record:
            record["_schema"] = record.pop("$schema")

        if "$language" in record:
            record["_language"] = self._normalize_language_code(
                record.pop("$language"),
                self.DEFAULT_LANGUAGE,
            )

        if "_language" not in record:
            record["_language"] = self.DEFAULT_LANGUAGE

        # Normalize 'oneOf' fields that could be an array of values or
        # a bare value to always be stored as an array of values.
        for field in self.ARRAY_FIELDS:
            if field in record and not isinstance(record[field], list):
                record[field] = [record[field]]

        # Normalize 'url_multilingual_or_array' fields that could contain bare
        # urls to always be stored as 'url_multilingual' objects.
        for field in self.URL_MULTILINGUAL_FIELDS:
            if field in record:
                record[field] = self._normalize_url_multilingual(
                    record[field], record["_language"]
                )

        # Normalize keywords to lowercase and store as array of values
        if "keywords" in record and isinstance(record["keywords"], str):
            record["keywords"] = list(
                filter(
                    None,
                    (s.strip().lower() for s in record["keywords"].split(",")),
                )
            )

        # Clean available_ui_languages
        if "available_ui_languages" in record:
            clean_ui_langs = self._normalize_available_ui_languages(
                record["available_ui_languages"]
            )
            record["available_ui_languages"] = clean_ui_langs

        # Strip out any unknown fields. We are trying really, really hard to
        # keep any data that we can salvage even if the input is messed up.
        for field in list(record):
            if field not in self._valid_field_names():
                if field not in self.EXTRA_ALLOWED_FIELDS:
                    logger.debug("Deleting unexpected field '%s'", field)
                    del record[field]

        return record

    def _normalize_language_code(self, code, unknown=None):
        """Normalize a language code.

        - Convert to lowercase
        - Validate against language_data
        - Retry with successive subtags removed
        - Give up and return unknown code
        """
        if not isinstance(code, str):
            return unknown
        code = code.lower()
        if language_data.is_known(code):
            return code
        if "-" in code:
            parts = code.split("-")
            for parent in ["-".join(parts[:-x]) for x in range(1, len(parts))]:
                if language_data.is_known(parent):
                    return parent
        return unknown

    def _normalize_url_multilingual(self, values, default):
        """Normalize incoming url_multilingual formatting."""
        fixed = []
        for value in values:
            if isinstance(value, str) and value:
                fixed.append({"language": default, "url": value})
            elif value and value.get("url"):
                lang_raw = value.get("language")
                lang_clean = self._normalize_language_code(lang_raw, default)
                if lang_clean != lang_raw:
                    logger.info(
                        "Replacing unknown language '%s' with '%s'",
                        lang_raw,
                        lang_clean,
                    )
                    value["language"] = lang_clean
                fixed.append(value)
        return fixed

    def _normalize_available_ui_languages(self, values):
        """Normalize incoming available_ui_languages values."""
        in_langs = set(values)
        clean_langs = list(
            filter(
                None,
                (
                    self._normalize_language_code(lang, None)
                    for lang in in_langs
                ),
            )
        )
        clean_langs_set = set(clean_langs)
        if in_langs != clean_langs_set:
            for code in in_langs - clean_langs_set:
                logger.info(
                    "Discarding unknown language '%s' "
                    "from available_ui_languages",
                    code,
                )
            return clean_langs
        return values

    def get_create_or_revive(self, defaults=None, **kwargs):
        """Convenience method to find an existing record or create a new one.

        Similar to `get_or_create` but it will also find records which have
        been marked as soft deleted. If the record was soft deleted the
        deletion flag will be cleared, but not persisted.

        :returns: (tool (Tool), was_created (boolean), was_revived (boolean))
        :rtype: tuple
        """
        qs = self.all_with_deleted().filter(**kwargs).exclude(deleted=None)
        tool = qs.first()
        if tool:
            # Mark as undeleted but do not save
            tool.deleted = None
            return tool, False, True
        tool, created = self.get_or_create(**kwargs, defaults=defaults)
        return tool, created, False

    def from_toolinfo(self, record, creator, origin, comment=None):
        """Create or update a Tool using data from a toolinfo record.

        :param self: This manager
        :type self: ToolManager
        :param record: Toolinfo record. May be mutated as a side effect.
        :type record: dict
        :param creator: User creating/updating the record
        :type creator: settings.AUTH_USER_MODEL
        :param origin: Origin of this submission
        :type origin: str
        :param comment: User provided comment for this change
        :type comment: str
        :returns: (tool (Tool), was_created (boolean), has_changes (boolean))
        :rtype: tuple
        """
        record["created_by"] = creator
        record["modified_by"] = creator
        record["origin"] = origin

        record = self.normalize_toolinfo(record)

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(creator)
            if comment is not None:
                reversion.set_comment(comment)

            with auditlog_context(creator, comment):
                tool, created, revived = self.get_create_or_revive(
                    name=record["name"], defaults=record
                )
            if created:
                return tool, created, False

            # Compare input to prior model and decide if anything of note has
            # changed. Revived models are always considered changed.
            has_changes = revived

            for key, value in record.items():
                if key in self.VARIANT_FIELDS:
                    continue

                prior = getattr(tool, key)

                if value != prior:
                    if not revived and key in self.INVARIANT_FIELDS:
                        # Invariant fields are allowed to change when reviving
                        # a deleted record.
                        raise ValidationError(
                            _(
                                "Changing %(key)s after initial "
                                "object creation is not allowed"
                            ),
                            code="invariant",
                            params={"key": key},
                        )

                    if value == "" and prior is None:
                        # T293103: guard against blank as null storage
                        # conversion causing infinite empty diffs
                        continue

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
                with auditlog_context(creator, comment):
                    tool.save()

        return tool, False, has_changes


@reversion.register()
@registry.register()
class Tool(ExportModelOperationsMixin("tool"), SafeDeleteModel):
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
        validators=[validators.URLValidator(schemes=["http", "https"])],
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
        schema=schema.KEYWORDS,
    )
    author = BlankAsNullCharField(
        blank=True,
        max_length=255,
        null=True,
        help_text=_("The primary tool developer."),
    )
    repository = BlankAsNullCharField(
        blank=True,
        max_length=2047,
        null=True,
        help_text=_("A link to the repository where the tool code is hosted."),
    )
    subtitle = BlankAsNullCharField(
        blank=True,
        max_length=255,
        null=True,
        help_text=_(
            "Longer than the full title but shorter than the description. "
            "It should add some additional context to the title."
        ),
    )
    openhub_id = BlankAsNullCharField(
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
        help_text=_(
            "Alternate links to the tool or install documentation in "
            "different natural languages."
        ),
        schema=schema.schema_for("url_alternates"),
        validators=[validate_url_mutilingual_list],
    )
    bot_username = BlankAsNullCharField(
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
    replaced_by = BlankAsNullTextField(
        blank=True,
        max_length=2047,
        null=True,
        validators=[validators.URLValidator(schemes=["http", "https"])],
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
        help_text=_(
            "A string or array of strings describing the wiki(s) this tool "
            "can be used on. Use hostnames such as `zh.wiktionary.org`. Use "
            "asterisks as wildcards. For example, `*.wikisource.org` means "
            "'this tool works on all Wikisource wikis.' `*` means "
            "'this works on all wikis, including Wikimedia wikis.'"
        ),
        schema=schema.schema_for("for_wikis", oneof=0),
    )
    icon = BlankAsNullCharField(
        blank=True,
        max_length=2047,
        null=True,
        validators=[
            validators.RegexValidator(
                regex=r"^https://commons\.wikimedia\.org/wiki/File:.+\..+$"
            ),
        ],
        help_text=_(
            "A link to a Wikimedia Commons file description page for an icon "
            "that depicts the tool."
        ),
    )
    license = BlankAsNullCharField(  # noqa: A003
        blank=True,
        max_length=255,
        null=True,
        help_text=_(
            "The software license the tool code is available under. "
            "Use a standard SPDX license identifier like 'GPL-3.0-or-later'."
        ),
        validators=[validate_spdx],
    )
    sponsor = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_("Organization(s) that sponsored the tool's development."),
        schema=schema.schema_for("sponsor", oneof=1),
    )
    available_ui_languages = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_(
            "The language(s) the tool's interface has been translated into. "
            "Use ISO 639 language codes like `zh` and `scn`. If not defined "
            "it is assumed the tool is only available in English."
        ),
        schema=schema.schema_for("available_ui_languages", oneof=0),
        validators=[validate_language_code_list],
    )
    technology_used = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_(
            "A string or array of strings listing technologies "
            "(programming languages, development frameworks, etc.) used in "
            "creating the tool."
        ),
        schema=schema.schema_for("technology_used", oneof=1),
    )
    tool_type = BlankAsNullCharField(
        choices=TOOL_TYPE_CHOICES,
        blank=True,
        max_length=32,
        null=True,
        help_text=_(
            "The manner in which the tool is used. "
            "Select one from the list of options."
        ),
    )
    api_url = BlankAsNullTextField(
        blank=True,
        max_length=2047,
        null=True,
        validators=[validators.URLValidator(schemes=["http", "https"])],
        help_text=_("A link to the tool's API, if available."),
    )
    developer_docs_url = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_(
            "A link to the tool's developer documentation, if available."
        ),
        schema=schema.schema_for("developer_docs_url", oneof=0),
        validators=[validate_url_mutilingual_list],
    )
    user_docs_url = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_("A link to the tool's user documentation, if available."),
        schema=schema.schema_for("user_docs_url", oneof=0),
        validators=[validate_url_mutilingual_list],
    )
    feedback_url = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_(
            "A link to location where the tool's user can leave feedback."
        ),
        schema=schema.schema_for("feedback_url", oneof=0),
        validators=[validate_url_mutilingual_list],
    )
    privacy_policy_url = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_("A link to the tool's privacy policy, if available."),
        schema=schema.schema_for("privacy_policy_url", oneof=0),
        validators=[validate_url_mutilingual_list],
    )
    translate_url = BlankAsNullTextField(
        blank=True,
        max_length=2047,
        null=True,
        validators=[validators.URLValidator(schemes=["http", "https"])],
        help_text=_("A link to the tool's translation interface."),
    )
    bugtracker_url = BlankAsNullTextField(
        blank=True,
        max_length=2047,
        null=True,
        validators=[validators.URLValidator(schemes=["http", "https"])],
        help_text=_(
            "A link to the tool's bug tracker on GitHub, Bitbucket, "
            "Phabricator, etc."
        ),
    )
    _schema = BlankAsNullCharField(
        blank=True,
        max_length=32,
        null=True,
        help_text=_(
            "A URI identifying the jsonschema for this toolinfo.json record. "
            "This should be a short uri containing only the name and revision "
            "at the end of the URI path."
        ),
    )
    _language = BlankAsNullCharField(
        blank=True,
        max_length=16,
        null=True,
        validators=[validate_language_code],
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
        auto_now_add=True, editable=False, db_index=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(
        auto_now=True, editable=False, db_index=True
    )

    objects = ToolManager()

    def __str__(self):
        """Str repr"""
        return self.name

    @property
    def auditlog_label(self):
        """Get label for use in auditlog output."""
        return self.name


@functools.lru_cache(maxsize=1)
def get_tool_content_type_id():
    """Lookup the content_type_id for a Tool model."""
    return ContentType.objects.get_for_model(Tool).pk


@receiver(post_revision_commit)
def add_revision_to_tool(sender, revision, versions, **kwargs):  # noqa: W0613
    """Handle post_revision_commit signal."""
    ct_id = get_tool_content_type_id()
    for version in versions:
        if version.content_type.id == ct_id:
            # Find the latest LogEntry for this Tool
            log_entry = (
                LogEntry.objects.filter(
                    content_type=version.content_type,
                    object_id=version.object_id,
                )
                .order_by("-timestamp")
                .first()
            )
            # Decorate with the revision id
            log_entry.params["revision"] = version.id
            log_entry.save(update_fields=["params"])
