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
import datetime

from django.test import TestCase
from django.utils import timezone

from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from toolhub.apps.user.models import ToolhubUser

from .. import views


class ApplicationViewSetTest(TestCase):
    """Test ApplicationViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )
        cls.app = Application.objects.create(
            name="ApplicationViewSetTest",
            redirect_uris="https://example.org/oa2-callback",
            user=cls.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            skip_authorization=False,
        )

    def test_list(self):
        """Test list action."""
        req = APIRequestFactory().get("")
        force_authenticate(req)  # Ensure anon user
        view = views.ApplicationViewSet.as_view({"get": "list"})
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        app = response.data["results"][0]
        self.assertIn("name", app)
        self.assertIn("redirect_url", app)
        self.assertIn("client_id", app)
        self.assertNotIn("client_secret", app)
        self.assertIn("user", app)

    def test_retrieve(self):
        """Test retrieve action."""
        req = APIRequestFactory().get("")
        force_authenticate(req)  # Ensure anon user
        view = views.ApplicationViewSet.as_view({"get": "retrieve"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.app.name)

    def test_create_requires_auth(self):
        """Assert that create rejects un-authed users."""
        req = APIRequestFactory().post("")
        force_authenticate(req)  # Ensure anon user
        view = views.ApplicationViewSet.as_view({"post": "create"})
        response = view(req)
        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create action."""
        data = {
            "name": "test_create",
            "redirect_url": "https://example.org/test_create/oa2",
        }
        req = APIRequestFactory().post("", data=data)
        force_authenticate(req, self.user)
        view = views.ApplicationViewSet.as_view({"post": "create"})
        response = view(req)
        self.assertEqual(response.status_code, 201)
        self.assertIn("name", response.data)
        self.assertIn("redirect_url", response.data)
        self.assertIn("client_id", response.data)
        self.assertIn("client_secret", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["redirect_url"], data["redirect_url"])

    def test_destroy_requires_auth(self):
        """Assert that destroy fails for an un-authenticated user."""
        req = APIRequestFactory().delete("")
        force_authenticate(req)  # Ensure anon user
        view = views.ApplicationViewSet.as_view({"delete": "destroy"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(response.status_code, 401)

    def test_destroy_requires_owner(self):
        """Ensure that destroy fails for random user."""
        bad_user = ToolhubUser.objects.create_user(  # nosec: B106
            username="test_destroy_requires_owner",
            email="test@example.org",
            password="unused",
        )
        self.assertNotEqual(self.app.user, bad_user)

        req = APIRequestFactory().delete("")
        force_authenticate(req, bad_user)
        view = views.ApplicationViewSet.as_view({"delete": "destroy"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(response.status_code, 403)

    def test_destroy(self):
        """Test destroy action."""
        req = APIRequestFactory().delete("")
        force_authenticate(req, self.user)
        view = views.ApplicationViewSet.as_view({"delete": "destroy"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(self.app.user, self.user)
        self.assertEqual(response.status_code, 204)

    def test_partial_update_requires_auth(self):
        """Assert that partial_update fails for an un-authenticated user."""
        req = APIRequestFactory().patch("")
        force_authenticate(req)  # Ensure anon user
        view = views.ApplicationViewSet.as_view({"patch": "partial_update"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(response.status_code, 401)

    def test_partial_update_requires_owner(self):
        """Ensure that partial_update fails for random user."""
        bad_user = ToolhubUser.objects.create_user(  # nosec: B106
            username="test_partial_update_requires_owner",
            email="test@example.org",
            password="unused",
        )
        self.assertNotEqual(self.app.user, bad_user)

        req = APIRequestFactory().patch("")
        force_authenticate(req, bad_user)
        view = views.ApplicationViewSet.as_view({"patch": "partial_update"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(response.status_code, 403)

    def test_partial_update(self):
        """Test partial_update."""
        url = "https://example.org/test_partial_update/"
        req = APIRequestFactory().patch("", {"redirect_url": url})
        force_authenticate(req, self.user)
        view = views.ApplicationViewSet.as_view({"patch": "partial_update"})
        response = view(req, client_id=self.app.client_id)
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.data)
        self.assertIn("redirect_url", response.data)
        self.assertIn("client_id", response.data)
        self.assertNotIn("client_secret", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["redirect_url"], url)


class AuthorizationViewSetTest(TestCase):
    """Test AuthorizationViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )
        cls.app = Application.objects.create(
            name="ApplicationViewSetTest",
            redirect_uris="https://example.org/oa2-callback",
            user=cls.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            skip_authorization=False,
        )
        cls.token = AccessToken.objects.create(  # nosec: B106
            user=cls.user,
            token="1234567890",
            application=cls.app,
            expires=timezone.now() + datetime.timedelta(days=1),
            scope="read write",
        )

    def test_list_requires_auth(self):
        """Assert that list fails for an un-authenticated user."""
        req = APIRequestFactory().get("")
        force_authenticate(req)  # Ensure anon user
        view = views.AuthorizationViewSet.as_view({"get": "list"})
        response = view(req)
        self.assertEqual(response.status_code, 401)

    def test_list_empty_for_random(self):
        """Ensure that list returns nothing for a random user."""
        bad_user = ToolhubUser.objects.create_user(  # nosec: B106
            username="test_list_empty_for_random",
            email="test@example.org",
            password="unused",
        )
        self.assertNotEqual(self.app.user, bad_user)
        req = APIRequestFactory().get("")
        force_authenticate(req, bad_user)
        view = views.AuthorizationViewSet.as_view({"get": "list"})
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list(self):
        """Test list."""
        req = APIRequestFactory().get("")
        force_authenticate(req, self.user)
        view = views.AuthorizationViewSet.as_view({"get": "list"})
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        token = response.data["results"][0]
        self.assertIn("id", token)
        self.assertIn("user", token)
        self.assertEqual(token["user"]["id"], self.user.pk)
        self.assertIn("application", token)
        self.assertEqual(token["application"]["name"], self.app.name)
        self.assertIn("created", token)
        self.assertIn("updated", token)
        self.assertIn("expires", token)
