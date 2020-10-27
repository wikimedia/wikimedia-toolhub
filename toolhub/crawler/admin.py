# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free oftware: you can redistribute it and/or modify
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

from . import models


@django.contrib.admin.register(models.CrawledUrl)
class CrawledUrlAdmin(django.contrib.admin.ModelAdmin):
    """Register with admin."""

    list_display = (
        "url",
        "created_by",
    )
    list_filter = ("created_by",)
    ordering = ("url",)
