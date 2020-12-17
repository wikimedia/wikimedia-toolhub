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
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from toolhub.apps.auditlog.signals import registry

from .validators import MediaWikiUsernameValidator


@registry.register()
class ToolhubUser(AbstractUser):
    """Local user model for Toolhub."""

    username_validator = MediaWikiUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=255,
        unique=True,
        help_text=_("Required. 255 characters or fewer."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = None
    last_name = None

    @property
    def auditlog_label(self):
        """Get label for use in auditlog output."""
        return self.username
