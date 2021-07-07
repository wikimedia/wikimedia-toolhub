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
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path

from drf_spectacular.views import SpectacularAPIView

from oauth2_provider.urls import base_urlpatterns as oauth2_patterns

from toolhub.apps.user.views import CurrentUserView
from toolhub.apps.user.views import LocaleView

from .routers import crawler_runs
from .routers import groups
from .routers import list_revisions
from .routers import root
from .routers import tool_revisions


api_patterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("user/", CurrentUserView.as_view(), name="user"),
    path("user/locale/", LocaleView.as_view(), name="locale"),
    path("", include(root.urls)),
    path("", include(crawler_runs.urls)),
    path("", include(groups.urls)),
    path("", include(tool_revisions.urls)),
    path("", include(list_revisions.urls)),
]

urlpatterns = [
    path("", include("vue.urls", namespace="vue")),
    path("admin/", admin.site.urls),
    path("api/", include((api_patterns, "api"), namespace="api")),
    path(
        "o/",
        include(
            (oauth2_patterns, "oauth2_provider"), namespace="oauth2_provider"
        ),
    ),
    path("social/", include("social_django.urls", namespace="social")),
    path("user/", include("toolhub.apps.user.urls", namespace="user")),
]

# Add development mode static files view
# NOTE: this only works with settings.DEBUG=True which should **never** be
# true in a production deployment.
urlpatterns += staticfiles_urlpatterns()
