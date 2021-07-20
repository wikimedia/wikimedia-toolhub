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
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prometheus.models import ExportModelOperationsMixin

import reversion


class RevisionMetadata(ExportModelOperationsMixin("revision"), models.Model):
    """Additional metadata to attach to a reversion revision.

    Use by calling `reversion.add_meta(RevisionMetadata, ...)` inside an
    active revision block.
    """

    revision = models.OneToOneField(
        reversion.models.Revision,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="meta",
    )
    suppressed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Has this revision been marked as hidden?"),
    )
    patrolled = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Has this revision been reviewed by a patroller?"),
    )
