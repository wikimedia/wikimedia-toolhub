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
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


def login(request):  # noqa: W0613 unused argument
    """Start the login process."""
    return redirect(reverse("social:begin", kwargs={"backend": "wikimedia"}))


def logout(request):
    """End the user's session."""
    auth_logout(request)
    return redirect(reverse("vue:main"))


def info(request):
    """Get information about the currently logged in user."""
    user = request.user
    user_info = {
        "username": user.get_username(),
        "email": getattr(user, "email", None),
        "is_active": user.is_active,
        "is_anonymous": user.is_anonymous,
        "is_authenticated": user.is_authenticated,
        "is_staff": user.is_staff,
    }
    # TODO: add social auth bits?
    return JsonResponse({"user": user_info})
