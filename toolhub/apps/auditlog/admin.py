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
import django.contrib.admin

from toolhub.admin import ReadOnlyModelAdmin

from . import models


@django.contrib.admin.register(models.LogEntry)
class LogEntryAdmin(ReadOnlyModelAdmin):
    """Register with admin."""

    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_pk",
        "action",
    )
    list_filter = ("user", "content_type")
    ordering = ("-action_time",)
