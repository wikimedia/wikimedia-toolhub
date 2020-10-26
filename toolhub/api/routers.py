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
from rest_framework import routers as drf_routers

from . import views


class ToolhubApiRootView(drf_routers.APIRootView):
    """Welcome to the API for Toolhub.

    This API provides access to Toolhub content and data in machine-readable
    formats.
    """


class Router(drf_routers.DefaultRouter):
    """Custom router."""

    APIRootView = ToolhubApiRootView


v1_router = Router()
v1_router.register("users", views.UserViewSet)
v1_router.register("groups", views.GroupViewSet)
