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
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token

from toolhub.tests import TestCase

from .. import serializers


class CurrentUserViewTest(TestCase):
    """Test CurrentUserView."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")

    def test_get_anon(self):
        """Test get as an un-authenticated user."""
        self.client.force_authenticate(user=None)

        url = "/api/user/"
        response = self.client.get(url)

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
        self.client.force_authenticate(user=self.user)

        url = "/api/user/"
        response = self.client.get(url)

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
        cls.user = cls._user("user")

    def test_get_as_anon(self):
        """Test get."""
        self.client.force_authenticate(user=None)

        url = "/api/user/locale/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "en")

    def test_get(self):
        """Test get."""
        self.client.force_authenticate(user=self.user)

        url = "/api/user/locale/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "en")

    def test_post_as_anon(self):
        """Test post as anon user."""
        self.client.force_authenticate(user=None)

        url = "/api/user/locale/"
        payload = {"language": "fj"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "fj")

    def test_post(self):
        """Test post."""
        self.client.force_authenticate(user=self.user)

        url = "/api/user/locale/"
        payload = {"language": "fj"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("language", response.data)
        self.assertEqual(response.data["language"], "fj")


class UserViewSetTest(TestCase):
    """Test UserViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")

    def test_list(self):
        """Test list action."""
        self.client.force_authenticate(user=None)

        url = "/api/users/"
        response = self.client.get(url)

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
        self.client.force_authenticate(user=None)

        url = "/api/users/{id}/".format(id=self.user.pk)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["id"], self.user.pk)
        self.assertIn("username", response.data)
        self.assertIn("groups", response.data)
        self.assertIn("date_joined", response.data)
        self.assertIn("social_auth", response.data)


class GroupMembersViewSetTest(TestCase):
    """Test GroupMembersViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")
        cls.crat = cls._user("Bureaucrat", "Bureaucrats")
        cls.admin = cls._user("Admin", "Administrators")
        cls.admin_group = Group.objects.get(name="Administrators")

    def test_update_requires_auth(self):
        """Assert that update fails for anon user."""
        self.client.force_authenticate(user=None)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.user.pk,
        )
        response = self.client.put(url)

        self.assertEqual(response.status_code, 401)

    def test_update_requires_perms(self):
        """Assert that update fails for random user."""
        self.client.force_authenticate(user=self.user)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.user.pk,
        )
        response = self.client.put(url)

        self.assertEqual(response.status_code, 403)

    def test_update_as_bureaucrat(self):
        """Assert that a Bureaucrat can add to a group."""
        self.client.force_authenticate(user=self.crat)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.user.pk,
        )
        response = self.client.put(url)

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
        self.client.force_authenticate(user=self.admin)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.user.pk,
        )
        response = self.client.put(url)

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
        self.client.force_authenticate(user=None)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.admin.pk,
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)

    def test_destroy_requires_perms(self):
        """Assert that destroy fails for random user."""
        self.client.force_authenticate(user=self.user)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.admin.pk,
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)

    def test_destroy_as_bureaucrat(self):
        """Assert that a Bureaucrat can remove from a group."""
        self.client.force_authenticate(user=self.crat)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.admin.pk,
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data)
        users = response.data["users"]
        self.assertEqual(len(users), 0)

    def test_destroy_as_admin(self):
        """Assert that an Admin can remove from a group."""
        self.client.force_authenticate(user=self.admin)

        url = "/api/groups/{group_pk}/members/{id}/".format(
            group_pk=self.admin_group.pk,
            id=self.admin.pk,
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data)
        users = response.data["users"]
        self.assertEqual(len(users), 0)


class AuthTokenViewTest(TestCase):
    """Test AuthTokenView."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")

    def test_get_requires_auth(self):
        """GET requires auth."""
        self.client.force_authenticate(user=None)

        url = "/api/user/authtoken/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)

    def test_get_without_create(self):
        """Test GET as an authenticated user with no token in db."""
        self.client.force_authenticate(user=self.user)

        url = "/api/user/authtoken/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get(self):
        """Test GET as an authenticated user."""
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)

        url = "/api/user/authtoken/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["token"], token.key)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["id"], self.user.pk)

    def test_post_requires_auth(self):
        """POST requires auth."""
        self.client.force_authenticate(user=None)

        url = "/api/user/authtoken/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, 401)

    def test_post(self):
        """POST creates new token."""
        self.client.force_authenticate(user=self.user)

        url = "/api/user/authtoken/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data["token"], token.key)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["id"], self.user.pk)

    def test_delete_requires_auth(self):
        """DELETE requires auth."""
        self.client.force_authenticate(user=None)

        url = "/api/user/authtoken/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)

    def test_delete_without_create(self):
        """Test DELETE as an authenticated user with no token in db."""
        self.client.force_authenticate(user=self.user)

        url = "/api/user/authtoken/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        """Test DELETE as an authenticated user."""
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)

        url = "/api/user/authtoken/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
