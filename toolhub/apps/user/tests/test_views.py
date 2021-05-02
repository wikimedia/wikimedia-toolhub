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
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from .. import models
from .. import views


class CurrentUserViewTest(TestCase):
    """Test CurrentUserView."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = models.ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )

    def test_get_anon(self):
        """Test get as an un-authenticated user."""
        req = APIRequestFactory().get("")
        force_authenticate(req, user=AnonymousUser())
        view = views.CurrentUserView.as_view()
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.data)
        self.assertEqual(response.data["username"], "")
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], None)
        self.assertIn("is_active", response.data)
        self.assertEqual(response.data["is_active"], False)
        self.assertIn("is_anonymous", response.data)
        self.assertEqual(response.data["is_anonymous"], True)
        self.assertIn("is_authenticated", response.data)
        self.assertEqual(response.data["is_authenticated"], False)
        self.assertIn("csrf_token", response.data)

    def test_get(self):
        """Test get as an authenticated user."""
        req = APIRequestFactory().get("")
        force_authenticate(req, user=self.user)
        view = views.CurrentUserView.as_view()
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.data)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertIn("is_active", response.data)
        self.assertEqual(response.data["is_active"], self.user.is_active)
        self.assertIn("is_anonymous", response.data)
        self.assertEqual(response.data["is_anonymous"], False)
        self.assertIn("is_authenticated", response.data)
        self.assertEqual(response.data["is_authenticated"], True)
        self.assertIn("csrf_token", response.data)


class LocaleViewTest(TestCase):
    """Test LocaleView."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = models.ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )

        cls.request_factory = APIRequestFactory()
        cls.session_middleware = SessionMiddleware()

    @classmethod
    def make_request(cls, method, route, *args, **kwargs):
        """Make a request object."""
        func = getattr(cls.request_factory, method)
        req = func(route, *args, **kwargs)
        cls.session_middleware.process_request(req)
        req.session.save()
        return req

    def test_get_as_anon(self):
        """Test get."""
        req = self.make_request("get", "")
        force_authenticate(req, user=AnonymousUser())
        view = views.LocaleView.as_view()
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "en-us")

    def test_get(self):
        """Test get."""
        req = self.make_request("get", "")
        force_authenticate(req, user=self.user)
        view = views.LocaleView.as_view()
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "en-us")

    def test_post_as_anon(self):
        """Test post as anon user."""
        req = self.make_request("post", "", {"language": "fj"})
        force_authenticate(req, user=AnonymousUser())
        view = views.LocaleView.as_view()
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "fj")

    def test_post(self):
        """Test post."""
        req = self.make_request("post", "", {"language": "fj"})
        force_authenticate(req, user=self.user)
        view = views.LocaleView.as_view()
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "fj")


class UserViewSetTest(TestCase):
    """Test UserViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = models.ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )

    def test_list(self):
        """Test list action."""
        req = APIRequestFactory().get("")
        force_authenticate(req, user=AnonymousUser())
        view = views.UserViewSet.as_view({"get": "list"})
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        user = response.data["results"][0]
        self.assertIn("id", user)
        self.assertEqual(user["id"], self.user.pk)
        self.assertIn("username", user)
        self.assertIn("groups", user)
        self.assertIn("date_joined", user)
        self.assertIn("social_auth", user)

    def test_retrieve(self):
        """Test retrieve action."""
        req = APIRequestFactory().get("")
        force_authenticate(req, user=AnonymousUser())
        view = views.UserViewSet.as_view({"get": "retrieve"})
        response = view(req, pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
