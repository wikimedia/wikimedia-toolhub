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
import contextlib

from .context import auditlog_user


class LogEntryUserMiddleware:
    """Associate the request's user with LogEntry objects."""

    def __init__(self, get_response):
        """Setup middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Associate the request's user with LogEntry objects."""
        context = contextlib.nullcontext()
        if hasattr(request, "user"):
            if getattr(request.user, "is_authenticated", False):
                context = auditlog_user(request.user)
        with context:
            return self.get_response(request)
