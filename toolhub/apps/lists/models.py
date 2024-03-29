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
from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prometheus.models import ExportModelOperationsMixin

import reversion

from safedelete.models import SafeDeleteModel

from toolhub.apps.auditlog.signals import registry
from toolhub.apps.toolinfo.models import Tool
from toolhub.fields import BlankAsNullCharField
from toolhub.fields import BlankAsNullTextField
from toolhub.fields import JSONSchemaField


@reversion.register()
@registry.register()
class ToolList(ExportModelOperationsMixin("list"), SafeDeleteModel):
    """A list of tools."""

    title = models.CharField(
        max_length=255,
        help_text=_("Title of this list"),
    )
    description = BlankAsNullTextField(
        blank=True,
        null=True,
        max_length=65535,
        help_text=_("Description of the list's theme or contents."),
    )
    icon = BlankAsNullCharField(
        blank=True,
        null=True,
        max_length=2047,
        validators=[
            validators.RegexValidator(
                regex=r"^https://commons\.wikimedia\.org/wiki/File:.+\..+$"
            ),
        ],
        help_text=_(
            "A link to a Wikimedia Commons file description page for an icon "
            "that depicts the list."
        ),
    )
    favorites = models.BooleanField(
        default=False,
        help_text=_(
            """If true, this list is a collection of the owning user's """
            """'favorite' tools."""
        ),
    )
    published = models.BooleanField(
        default=False,
        help_text=_("If true, this list is visible to everyone."),
    )
    featured = models.BooleanField(
        default=False,
        help_text=_("If true, this list has been marked as featured."),
    )
    tools = models.ManyToManyField(
        Tool,
        through="ToolListItem",
    )
    # The tool_names member is parallel tracking of the m2m `tools`
    # collection contents. This bit of clunkiness is needed for tracking
    # and reporting the point in time list contents using reversion.
    tool_names = JSONSchemaField(
        blank=True,
        default=list,
        help_text=_("List of the names of the tools in this list."),
        schema={
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lists",
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

    class Meta:
        """Configure model."""

        constraints = [
            models.UniqueConstraint(
                fields=["created_by"],
                condition=models.Q(favorites=True),
                name="unique_favorites_user",
            ),
        ]
        verbose_name = "toollist"

        # Do not generate auditlog entries when the instance represents a list
        # of user's favorites.
        toolhub_auditlog_exclude = {
            "favorites": True,
        }

    def __str__(self):
        """Str repr"""
        return self.title

    @property
    def auditlog_label(self):
        """Get label for use in auditlog output."""
        return self.title


class ToolListItemManager(models.Manager):
    """Custom manager for ToolListItem models."""

    def get_user_favorites(self, user):
        """Get the user's favorites list."""
        favorites, _ = ToolList.objects.get_or_create(
            created_by=user,
            favorites=True,
            defaults={
                "title": "Favorites",
            },
        )
        return favorites


class ToolListItem(ExportModelOperationsMixin("listitem"), models.Model):
    """Many-to-many tracking of Tool models contained by a ToolList."""

    toollist = models.ForeignKey(ToolList, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Position of this tool in the list."),
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.SET_NULL,
    )
    added_date = models.DateTimeField(
        auto_now_add=True, editable=False, db_index=True
    )

    objects = ToolListItemManager()

    class Meta:
        """Model config"""

        constraints = [
            models.UniqueConstraint(
                fields=["toollist", "tool"],
                name="unique_item",
            ),
        ]
        ordering = (
            "order",
            "added_date",
        )

    def __str__(self):
        """Str repr"""
        return self.tool.name

    def natural_key(self):
        """Natural reference."""
        return (self.toollist, self.tool)
