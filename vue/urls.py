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
from django.urls import path

from .views import main

app_name = "vue"  # noqa: C0103
urlpatterns = [
    path("", main, name="main"),
    path("add-or-remove-tools", main, name="add-or-remove-tools"),
    path("lists", main, name="lists"),
    path("lists/create", main, name="lists-create"),
    path("list/<path:path>", main, name="list"),
    path("api-docs", main, name="api-docs"),
    path("audit-logs", main, name="audit-logs"),
    path("crawler-history", main, name="crawler-history"),
    path("developer-settings", main, name="developer-settings"),
    path("members", main, name="members"),
    path("tool/<path:path>", main, name="tool"),
    path("search", main, name="search"),
]
