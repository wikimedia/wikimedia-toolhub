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
from django.conf import settings


class FLoCOptOutMiddleware:
    """Add FLoC opt-out header to responses.

    https://github.com/wicg/floc#opting-out-of-computation
    """

    header = "Permissions-Policy"
    payload = "interest-cohort=()"

    def __init__(self, get_response):
        """Configure middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Add FLoC opt-out header to responses."""
        response = self.get_response(request)
        if self.header not in response:
            response[self.header] = self.payload
        return response


class ReferrerPolicyMiddleware:
    """Add a Referrer-Policy header to responses.

    https://www.w3.org/TR/referrer-policy/
    """

    header = "Referrer-Policy"

    def __init__(self, get_response):
        """Configure middleware."""
        self.get_response = get_response
        self.payload = getattr(settings, "REFERRER_POLICY", "strict-origin")

    def __call__(self, request):
        """Add Referrer-Policy header to responses."""
        response = self.get_response(request)
        if self.header not in response:
            response[self.header] = self.payload
        return response
