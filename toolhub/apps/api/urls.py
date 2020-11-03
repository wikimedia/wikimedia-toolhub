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
from django.urls import include
from django.urls import path

from drf_spectacular.views import SpectacularAPIView

from .routers import router
from .views.user import CurrentUserView


app_name = "toolhub.api"
urlpatterns = [
    path(".schema", SpectacularAPIView.as_view(), name="schema"),
    path("user/", CurrentUserView.as_view(), name="user"),
    path("", include(router.urls)),
]
