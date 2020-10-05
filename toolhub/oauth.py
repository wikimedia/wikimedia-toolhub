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
import logging

from django.conf import settings

from social_core.backends.oauth import BaseOAuth2


logger = logging.getLogger(__name__)


class WikimediaOAuth2(BaseOAuth2):
    """Wikimedia OAuth2 authentication backend."""

    name = "wikimedia"
    BASE_URL = settings.SOCIAL_AUTH_WIKIMEDIA_BASE_URL
    AUTHORIZATION_URL = BASE_URL + "/oauth2/authorize"
    ACCESS_TOKEN_URL = BASE_URL + "/oauth2/access_token"
    REFRESH_TOKEN_URL = ACCESS_TOKEN_URL
    ACCESS_TOKEN_METHOD = "POST"
    STATE_PARAMETER = "state"
    REDIRECT_STATE = False
    ID_KEY = "sub"
    EXTRA_DATA = [
        ("editcount", "editcount"),
        ("confirmed_email", "confirmed_email"),
        ("blocked", "blocked"),
        ("registered", "registered"),
        ("groups", "groups"),
        ("rights", "rights"),
        ("grants", "grants"),
    ]

    def get_user_details(self, response):
        """Extract user details from response."""
        return {
            "username": response["username"],
            "email": response["email"] or None,
            "fullname": response["realname"] or None,
        }

    def user_data(self, access_token, *args, **kwargs):
        """Load user data from service."""
        return self.get_json(
            self.BASE_URL + "/oauth2/resource/profile",
            headers={
                "Authorization": "Bearer {}".format(access_token),
            },
        )
