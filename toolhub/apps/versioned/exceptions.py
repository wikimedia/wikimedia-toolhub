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
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class ConflictingState(APIException):
    """Patch failed due to conflicting state."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Failed to apply patch.")


class CurrentRevision(APIException):
    """Suppression failed for HEAD revision."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("Current revision cannot be hidden.")
    default_code = "current_revision"


class SuppressedRevision(APIException):
    """Diff failed due to a suppressed revision."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("Missing content for one or more revisions.")
    default_code = "suppressed_revision"
