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
from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from toolhub.apps.user.models import ToolhubUser

from .. import models
from .. import views


class UrlViewSetTest(TestCase):
    """Test UrlViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )

        cls.url = models.Url.objects.create(
            url="https://example.org/test",
            created_by=cls.user,
        )

    def test_list(self):
        """Test list action."""
        req = APIRequestFactory().get("")
        force_authenticate(req)  # Ensure anon user
        view = views.UrlViewSet.as_view({"get": "list"})
        response = view(req)
        self.assertEqual(response.status_code, 200)

    def test_retrieve(self):
        """Test retrieve action."""
        req = APIRequestFactory().get("")
        force_authenticate(req)  # Ensure anon user
        view = views.UrlViewSet.as_view({"get": "retrieve"})
        response = view(req, pk=self.url.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_requires_auth(self):
        """Ensure that create fails for an un-authenticated user."""
        req = APIRequestFactory().post("")
        force_authenticate(req)  # Ensure anon user
        view = views.UrlViewSet.as_view({"post": "create"})
        response = view(req)
        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create action."""
        url = "https://example.org/test_create"
        req = APIRequestFactory().post("", {"url": url})
        force_authenticate(req, self.user)
        view = views.UrlViewSet.as_view({"post": "create"})
        response = view(req)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["url"], url)

    def test_create_rejects_duplicate_url(self):
        """Ensure that create errors when attempting to insert duplicate."""
        url = self.url.url
        req = APIRequestFactory().post("", {"url": url})
        force_authenticate(req, self.user)
        view = views.UrlViewSet.as_view({"post": "create"})
        response = view(req)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "1000")
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(response.data["errors"][0]["code"], "3001")

    def test_destroy_requires_auth(self):
        """Ensure that destroy fails for an un-authenticated user."""
        req = APIRequestFactory().delete("")
        force_authenticate(req)  # Ensure anon user
        view = views.UrlViewSet.as_view({"delete": "destroy"})
        response = view(req, pk=self.url.pk)
        self.assertEqual(response.status_code, 401)

    def test_destroy_requires_owner(self):
        """Ensure that destroy fails for random user."""
        bad_user = ToolhubUser.objects.create_user(  # nosec: B106
            username="test_destroy_requires_owner",
            email="test@example.org",
            password="unused",
        )
        req = APIRequestFactory().delete("")
        force_authenticate(req, bad_user)
        view = views.UrlViewSet.as_view({"delete": "destroy"})

        self.assertNotEqual(self.url.created_by, bad_user)
        self.assertEqual(self.url.created_by, self.user)

        response = view(req, pk=self.url.pk)
        self.assertEqual(response.status_code, 403)

    def test_destroy(self):
        """Test destroy action."""
        req = APIRequestFactory().delete("")
        force_authenticate(req, self.user)
        view = views.UrlViewSet.as_view({"delete": "destroy"})

        self.assertEqual(self.url.created_by, self.user)

        response = view(req, pk=self.url.pk)
        self.assertEqual(response.status_code, 204)

    def test_self_requires_auth(self):
        """Assert that you must be logged in to call self"""
        req = APIRequestFactory().get("")
        force_authenticate(req)  # Ensure anon user
        view = views.UrlViewSet.as_view({"get": "self"})
        response = view(req)
        self.assertEqual(response.status_code, 401)

    def test_self_empty(self):
        """Assert that self list is empty when user owns no urls."""
        bad_user = ToolhubUser.objects.create_user(  # nosec: B106
            username="test_self_empty",
            email="test@example.org",
            password="unused",
        )
        req = APIRequestFactory().get("")
        force_authenticate(req, bad_user)
        view = views.UrlViewSet.as_view({"get": "self"})
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_self(self):
        """Test self action"""
        req = APIRequestFactory().get("")
        force_authenticate(req, self.user)
        view = views.UrlViewSet.as_view({"get": "self"})
        response = view(req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
