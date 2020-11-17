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
import json

from social_core.tests.backends.oauth import OAuth2Test


class WikimediaOAuth2Test(OAuth2Test):
    """Test WikimediaOAuth2."""

    backend_path = "toolhub.oauth.WikimediaOAuth2"
    user_data_url = (
        "https://meta.wikimedia.org/w/rest.php/oauth2/resource/profile"
    )
    expected_username = "😂"

    access_token_body = json.dumps(
        {
            "token_type": "Bearer",
            "expires_in": 9223371259704000000,
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
        }
    )
    user_data_body = json.dumps(
        {
            "sub": 12345,
            "username": expected_username,
            "editcount": 54321,
            "confirmed_email": True,
            "blocked": False,
            "registered": "19700101000000",
            "groups": ["*"],
            "rights": ["read", "writeapi"],
            "grants": ["basic", "privateinfo"],
            "realname": "",
            "email": "demo@example.org",
        }
    )
    refresh_token_body = json.dumps(
        {
            "token_type": "Bearer",
            "expires_in": 9223371259704000000,
            "access_token": "mock-new-access-token",
            "refresh_token": "mock-new-refresh-token",
        }
    )

    def extra_settings(self):
        """Inject these settings into test runs."""
        # TODO: figure out why these settings are not picked up from the
        # Toolhub settings module during test runs.
        return {
            "SOCIAL_AUTH_CLEAN_USERNAMES": False,
            "SOCIAL_AUTH_SLUGIFY_USERNAMES": False,
        }

    def test_login(self):
        """Test the login flow."""
        self.do_login()

    def test_partial_pipeline(self):
        """Test the partial pipeline flow."""
        self.do_partial_pipeline()

    def test_refresh_token(self):
        """Test the refresh token flow."""
        user, social = self.do_refresh_token()
        self.assertEqual(user.username, self.expected_username)
        self.assertEqual(
            social.extra_data["access_token"], "mock-new-access-token"
        )
