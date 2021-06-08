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
from django.contrib.auth.models import Group
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from .. import models
from .. import serializers
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

    def test_get_as_anon(self):
        """Test get."""
        client = APIClient()
        client.force_authenticate(user=None)
        response = client.get("/api/user/locale/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "en")

    def test_get(self):
        """Test get."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get("/api/user/locale/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "en")

    def test_post_as_anon(self):
        """Test post as anon user."""
        client = APIClient()
        client.force_authenticate(user=None)
        response = client.post("/api/user/locale/", {"language": "fj"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "fj")

    def test_post(self):
        """Test post."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post("/api/user/locale/", {"language": "fj"})
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


class GroupMembersViewSetTest(TestCase):
    """Test GroupMembersViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = models.ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )
        cls.crat = models.ToolhubUser.objects.create_user(  # nosec: B106
            username="Bureaucrat",
            email="crat@example.org",
            password="unused",
        )
        Group.objects.get(name="Bureaucrats").user_set.add(cls.crat)
        cls.admin = models.ToolhubUser.objects.create_user(  # nosec: B106
            username="Admin",
            email="admin@example.org",
            password="unused",
        )
        Group.objects.get(name="Administrators").user_set.add(cls.admin)
        cls.admin_group = Group.objects.get(name="Administrators")

    def test_update_requires_auth(self):
        """Assert that update fails for anon user."""
        req = APIRequestFactory().put("")
        force_authenticate(req, user=AnonymousUser())
        view = views.GroupMembersViewSet.as_view({"put": "update"})
        response = view(req, group_pk=self.admin_group.pk, id=self.user.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_requires_perms(self):
        """Assert that update fails for random user."""
        req = APIRequestFactory().put("")
        force_authenticate(req, user=self.user)
        view = views.GroupMembersViewSet.as_view({"put": "update"})
        response = view(req, group_pk=self.admin_group.pk, id=self.user.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_as_bureaucrat(self):
        """Assert that a Bureaucrat can add to a group."""
        req = APIRequestFactory().put("")
        force_authenticate(req, user=self.crat)
        view = views.GroupMembersViewSet.as_view({"put": "update"})
        response = view(req, group_pk=self.admin_group.pk, id=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data)
        users = response.data["users"]
        self.assertEqual(
            users,
            [
                serializers.UserSerializer(instance=self.admin).data,
                serializers.UserSerializer(instance=self.user).data,
            ],
        )

    def test_update_as_admin(self):
        """Assert that an Admin can add to a group."""
        req = APIRequestFactory().put("")
        force_authenticate(req, user=self.admin)
        view = views.GroupMembersViewSet.as_view({"put": "update"})
        response = view(req, group_pk=self.admin_group.pk, id=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data)
        users = response.data["users"]
        self.assertEqual(
            users,
            [
                serializers.UserSerializer(instance=self.admin).data,
                serializers.UserSerializer(instance=self.user).data,
            ],
        )

    def test_destroy_requires_auth(self):
        """Assert that destroy fails for anon user."""
        req = APIRequestFactory().delete("")
        force_authenticate(req, user=AnonymousUser())
        view = views.GroupMembersViewSet.as_view({"delete": "destroy"})
        response = view(req, group_pk=self.admin_group.pk, id=self.admin.pk)
        self.assertEqual(response.status_code, 403)

    def test_destroy_requires_perms(self):
        """Assert that destroy fails for random user."""
        req = APIRequestFactory().delete("")
        force_authenticate(req, user=self.user)
        view = views.GroupMembersViewSet.as_view({"delete": "destroy"})
        response = view(req, group_pk=self.admin_group.pk, id=self.admin.pk)
        self.assertEqual(response.status_code, 403)

    def test_destroy_as_bureaucrat(self):
        """Assert that a Bureaucrat can remove from a group."""
        req = APIRequestFactory().delete("")
        force_authenticate(req, user=self.crat)
        view = views.GroupMembersViewSet.as_view({"delete": "destroy"})
        response = view(req, group_pk=self.admin_group.pk, id=self.admin.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data)
        users = response.data["users"]
        self.assertEqual(len(users), 0)

    def test_destroy_as_admin(self):
        """Assert that an Admin can remove from a group."""
        req = APIRequestFactory().delete("")
        force_authenticate(req, user=self.admin)
        view = views.GroupMembersViewSet.as_view({"delete": "destroy"})
        response = view(req, group_pk=self.admin_group.pk, id=self.admin.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data)
        users = response.data["users"]
        self.assertEqual(len(users), 0)
