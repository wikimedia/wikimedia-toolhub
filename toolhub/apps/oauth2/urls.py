# Copyright (c) 2023 Wikimedia Foundation and contributors.
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

from oauth2_provider import views

from .views import AuthzView

urlpatterns = [
    path("authorize/", AuthzView.as_view(), name="authorize"),
    path("token/", views.TokenView.as_view(), name="token"),
    path(
        "revoke_token/", views.RevokeTokenView.as_view(), name="revoke-token"
    ),
    path(
        "introspect/", views.IntrospectTokenView.as_view(), name="introspect"
    ),
]
