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
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views.generic.base import RedirectView

from drf_spectacular.views import SpectacularAPIView

from toolhub.apps.oauth2.urls import urlpatterns as oauth2_patterns
from toolhub.apps.user.views import AuthTokenView
from toolhub.apps.user.views import CurrentUserView
from toolhub.apps.user.views import LocaleView

from vue.views import HomeView

from .routers import crawler_runs
from .routers import groups
from .routers import list_revisions
from .routers import root
from .routers import tool_revisions
from .views import csp_report
from .views import healthz
from .views import robots_txt


api_patterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("user/", CurrentUserView.as_view(), name="user"),
    path("user/authtoken/", AuthTokenView.as_view(), name="authtoken"),
    path("user/locale/", LocaleView.as_view(), name="locale"),
    path("ui/home/", HomeView.as_view(), name="api_ui_home"),
    path("", include(root.urls)),
    path("", include(crawler_runs.urls)),
    path("", include(groups.urls)),
    path("", include(tool_revisions.urls)),
    path("", include(list_revisions.urls)),
]

urlpatterns = [
    path("", include("vue.urls", namespace="vue")),
    path("", include("django_prometheus.urls")),  # /metrics
    path("admin/", admin.site.urls),
    path("api/", include((api_patterns, "api"), namespace="api")),
    path("csp-report", csp_report, name="csp_report"),
    path("healthz", healthz, name="healthz"),
    path(
        "o/",
        include(
            (oauth2_patterns, "oauth2_provider"), namespace="oauth2_provider"
        ),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("img/favicon-outline.ico")
        ),
        name="favicon",
    ),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("social/", include("social_django.urls", namespace="social")),
    path("user/", include("toolhub.apps.user.urls", namespace="user")),
]

# Add development mode static files view
# NOTE: this only works with settings.DEBUG=True which should **never** be
# true in a production deployment.
urlpatterns += staticfiles_urlpatterns()
