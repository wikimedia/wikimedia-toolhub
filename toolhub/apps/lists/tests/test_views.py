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
import json
import os

from django.contrib.auth.models import Group
from django.test import TestCase

from rest_framework.test import APIClient

import reversion
from reversion.models import Version

from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.user.models import ToolhubUser
from toolhub.apps.versioned.models import RevisionMetadata

from .. import models


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class ToolListViewSetTest(TestCase):
    """Test ToolListViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )

        with open(os.path.join(TEST_DIR, "toolinfo_fixture.json")) as fixture:
            cls.toolinfo = json.load(fixture)

        cls.tool, _, _ = Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, Tool.ORIGIN_API
        )

        cls.list = models.ToolList.objects.create(
            title="A test fixture list",
            published=True,
            created_by=cls.user,
        )
        models.ToolListItem.objects.create(
            toollist=cls.list,
            tool=cls.tool,
        )

    def test_create_requires_auth(self):
        """Assert that create fails for anon."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/"
        payload = {"title": "test", "tools": []}
        response = client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/"
        payload = {
            "title": "test",
            "tools": [self.tool.name],
            "comment": "test",
        }
        response = client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_validates_tool_names(self):
        """Ensure duplicate and non-existant tool names are rejected."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/"
        payload = {
            "title": "test",
            "tools": [
                "not valid",
                "no-such-tool",
                self.tool.name,
                self.tool.name,
            ],
        }
        response = client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.data)
        errors = response.data["errors"]
        self.assertEqual(len(errors), 2)
        for error in errors:
            self.assertIn("code", error)
            self.assertIn("field", error)
            self.assertIn("message", error)
            self.assertEqual(str(error["field"]), "tools")

    def test_update_requires_auth(self):
        """Assert that update requires authentication."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Update test",
            "tools": [],
            "comment": "unauthenticated update should fail",
        }
        response = client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_requires_creator(self):
        """Assert that update requires authentication."""
        new_user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Testy McTestface",
            email="test@example.net",
            password="unused",
        )
        client = APIClient()
        client.force_authenticate(user=new_user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Update test",
            "tools": [],
            "comment": "non-creator update should fail",
        }
        response = client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 404)

    def test_update(self):
        """Test update."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Update test",
            "tools": [],
            "comment": "remove a tool from the list",
        }
        response = client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.list.id)
        self.assertIn("tools", response.data)
        self.assertEqual(len(response.data["tools"]), 0)

    def test_destroy_requires_auth(self):
        """Assert that destroy requires auth."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_destroy(self):
        """Test destroy."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_list(self):
        """Test list."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/"
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("results", response.data)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.list.id)
        self.assertIn("tools", results[0])
        self.assertEqual(len(results[0]["tools"]), 1)
        self.assertEqual(results[0]["tools"][0]["name"], self.tool.name)

    def test_retrieve(self):
        """Test retrieve."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.id,
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.list.id)
        self.assertIn("tools", response.data)
        self.assertEqual(len(response.data["tools"]), 1)
        self.assertEqual(response.data["tools"][0]["name"], self.tool.name)

    def test_retrieve_ignores_unpublished(self):
        """Ensure that unpublished lists are not shown to non-owners."""
        self.list.published = False
        self.list.save()
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.id,
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 404)


class ToolListRevisionViewSetTest(TestCase):
    """Test ToolListRevisionViewSet."""

    @classmethod
    def versions(cls, toollist=None):
        """Get queryset over versions."""
        if toollist is None:
            toollist = cls.list
        return Version.objects.get_for_object(toollist)

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )
        cls.oversighter = ToolhubUser.objects.create_user(  # nosec: B106
            username="Oversighter",
            email="oversighter@example.org",
            password="unused",
        )
        Group.objects.get(name="Oversighters").user_set.add(cls.oversighter)
        cls.patroller = ToolhubUser.objects.create_user(  # nosec: B106
            username="Patroller",
            email="patroller@example.org",
            password="unused",
        )
        Group.objects.get(name="Patrollers").user_set.add(cls.patroller)

        with open(os.path.join(TEST_DIR, "toolinfo_fixture.json")) as fixture:
            cls.toolinfo = json.load(fixture)

        cls.tool, _, _ = Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, models.Tool.ORIGIN_API
        )

        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            reversion.set_user(cls.user)

            cls.list = models.ToolList.objects.create(
                title="A test fixture list",
                published=True,
                created_by=cls.user,
            )
            models.ToolListItem.objects.create(
                toollist=cls.list,
                tool=cls.tool,
            )

    def test_list(self):
        """Test list action."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/".format(
            list_pk=self.list.pk,
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve(self):
        """Test retrieve action."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_diff(self):
        """Test diff action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "Changed"
            self.list.save()

        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk
        self.assertNotEqual(diff_from, diff_to)

        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/diff/{other_id}/".format(
            list_pk=self.list.pk,
            id=diff_from,
            other_id=diff_to,
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("original", response.data)
        self.assertIn("operations", response.data)
        self.assertIn("result", response.data)

    def test_diff_suppressed_anon(self):
        """Test diff with suppressed start/end as anon."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "BAD FAITH"
            self.list.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()
        self.assertTrue(self.versions().last().revision.meta.suppressed)

        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk
        self.assertNotEqual(diff_from, diff_to)

        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/diff/{other_id}/".format(
            list_pk=self.list.pk,
            id=diff_from,
            other_id=diff_to,
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_diff_suppressed_priv(self):
        """Test diff with suppressed start/end as privledged user."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "BAD FAITH"
            self.list.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk
        self.assertNotEqual(diff_from, diff_to)

        client = APIClient()
        client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/diff/{other_id}/".format(
            list_pk=self.list.pk,
            id=diff_from,
            other_id=diff_to,
        )
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("original", response.data)
        self.assertIn("operations", response.data)
        self.assertIn("result", response.data)
        self.assertTrue(response.data["result"]["suppressed"])

    def test_revert_requires_auth(self):
        """Test revert action."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/revert/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_revert(self):
        """Test revert action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "Changed"
            self.list.save()
        self.assertEqual(self.list.title, "Changed")

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/revert/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_requires_auth(self):
        """Test undo action."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/undo/{other_id}/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
            other_id=self.versions().last().pk,
        )
        response = client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_undo(self):
        """Test undo action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "Changed"
            self.list.save()
        self.assertEqual(self.list.title, "Changed")

        undo_from = self.versions().first().pk
        undo_to = self.versions().last().pk
        self.assertNotEqual(undo_from, undo_to)

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/undo/{other_id}/".format(
            list_pk=self.list.pk,
            id=undo_from,
            other_id=undo_to,
        )
        response = client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_hide_requires_auth(self):
        """Test hide action."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 401)

    def test_hide_requires_special_rights(self):
        """Test hide action."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_hide_forbids_head(self):
        """Test hide action."""
        client = APIClient()
        client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["code"], 4091)

    def test_hide(self):
        """Test hide action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "REVERTED"
            self.list.save()

        client = APIClient()
        client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.versions()[1].revision.meta.suppressed)

    def test_reveal_requires_auth(self):
        """Test reveal action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "REVERTED"
            self.list.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 401)

    def test_reveal_requires_special_rights(self):
        """Test reveal action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "REVERTED"
            self.list.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=bad_faith.pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_reveal(self):
        """Test reveal action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "REVERTED"
            self.list.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        client = APIClient()
        client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=bad_faith.pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 204)

    def test_reveal_rejects_unhidden(self):
        """Test reveal action."""
        client = APIClient()
        client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 404)

    def test_patrol_requires_auth(self):
        """Test patrol action."""
        client = APIClient()
        client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 401)

    def test_patrol_requires_special_rights(self):
        """Test patrol action."""
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_patrol(self):
        """Test patrol action."""
        client = APIClient()
        client.force_authenticate(user=self.patroller)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 204)

    def test_patrol_rejects_patrolled(self):
        """Test patrol action."""
        p = self.versions().first()
        p.revision.meta.patrolled = True
        p.revision.meta.save()

        client = APIClient()
        client.force_authenticate(user=self.patroller)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = client.patch(url)
        self.assertEqual(response.status_code, 404)
