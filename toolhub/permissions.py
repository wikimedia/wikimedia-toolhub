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
from rest_framework import permissions


class IsAdminOrIsSelf(permissions.BasePermission):
    """Protect User objects from authorized changes."""

    def has_object_permission(self, request, view, obj):
        """Check permissions."""
        return request.user.is_staff or obj == request.user


class IsCreator(permissions.BasePermission):
    """Object-level permission to only allow creators of an object to edit it.

    Assumes the model instance has a `created_by` attribute.
    """

    def has_object_permission(self, request, view, obj):
        """Check permissions."""
        return request.user.is_staff or obj.created_by == request.user


class IsReadOnly(permissions.BasePermission):
    """Allow read-only requests."""

    def has_object_permission(self, request, view, obj):
        """Check permissions."""
        return request.method in permissions.SAFE_METHODS
