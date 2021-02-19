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
from rest_framework import routers as drf_routers

from rest_framework_nested import routers as nested_routers

import toolhub.apps.auditlog.views as auditlog_views
import toolhub.apps.crawler.views as crawler_views
import toolhub.apps.oauth2.views as oauth_views
import toolhub.apps.search.views as search_views
import toolhub.apps.toolinfo.views as toolinfo_views
import toolhub.apps.user.views as user_views


class ToolhubApiRootView(drf_routers.APIRootView):
    """Welcome to the API for Toolhub.

    This API provides access to Toolhub content and data in machine-readable
    formats.
    """


class Router(drf_routers.DefaultRouter):
    """Custom router."""

    APIRootView = ToolhubApiRootView


root = Router()
root.register("auditlogs", auditlog_views.LogEntryViewSet)
root.register("crawler/runs", crawler_views.RunViewSet)
root.register("crawler/urls", crawler_views.UrlViewSet)
root.register("groups", user_views.GroupViewSet)
root.register("oauth/applications", oauth_views.ApplicationViewSet)
root.register(
    "oauth/authorized",
    oauth_views.AuthorizationViewSet,
    basename="accesstoken",
)
root.register(
    "search/tools", search_views.ToolDocumentViewSet, basename="search-tools"
)
root.register("spdx", toolinfo_views.SpdxViewSet, basename="spdx")
root.register("tools", toolinfo_views.ToolViewSet, basename="tool")
root.register("users", user_views.UserViewSet)

crawler_runs = nested_routers.NestedSimpleRouter(
    root,
    "crawler/runs",
    lookup="run",
)
crawler_runs.register(
    "urls",
    crawler_views.RunUrlViewSet,
    basename="run-urls",
)

tool_revisions = nested_routers.NestedSimpleRouter(
    root,
    "tools",
    lookup="tool",
)
tool_revisions.register(
    "revisions",
    toolinfo_views.ToolRevisionViewSet,
    basename="tool-revisions",
)
