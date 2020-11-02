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
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path


urlpatterns = [
    path("", include("vue.urls", namespace="vue")),
    path("admin/", admin.site.urls),
    path("api/", include("toolhub.apps.api.urls", namespace="api")),
    path("social/", include("social_django.urls", namespace="social")),
    path("user/", include("toolhub.apps.user.urls", namespace="user")),
]

# Add development mode static files view
# NOTE: this only works with settings.DEBUG=True which should **never** be
# true in a production deployment.
urlpatterns += staticfiles_urlpatterns()
