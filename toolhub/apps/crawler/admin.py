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
from toolhub.admin import ReadOnlyTabularInline

from . import models


@django.contrib.admin.register(models.Url)
class UrlAdmin(django.contrib.admin.ModelAdmin):
    """Admin view of Url."""

    list_display = (
        "url",
        "created_by",
    )
    list_filter = ("created_by",)
    ordering = ("url",)


class RunUrlInline(ReadOnlyTabularInline):
    """Inline admin view of RunUrl."""

    model = models.RunUrl
    fields = (
        "url",
        "status_code",
        "valid",
        "redirected",
    )


@django.contrib.admin.register(models.Run)
class RunAdmin(ReadOnlyModelAdmin):
    """Admin view of a Run."""

    list_display = ("start_date",)
    ordering = ("start_date",)
    inlines = (RunUrlInline,)

    class Media:
        """Media overrides."""

        css = {"all": ("css/admin.css",)}
