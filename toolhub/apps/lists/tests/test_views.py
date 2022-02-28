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
import reversion
from reversion.models import Version

from toolhub.apps.toolinfo.models import Tool
from toolhub.apps.versioned.models import RevisionMetadata
from toolhub.tests import TestCase

from .. import models


class ToolListViewSetTest(TestCase):
    """Test ToolListViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")
        cls.administrator = cls._user("admin", group="Administrators")
        cls.oversighter = cls._user("oversighter", group="Oversighters")
        cls.toolinfo = cls._load_json("toolinfo_fixture.json")

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
        self.client.force_authenticate(user=None)
        url = "/api/lists/"
        payload = {"title": "test", "tools": []}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create."""
        self.client.force_authenticate(user=self.user)
        url = "/api/lists/"
        payload = {
            "title": "test",
            "tools": [self.tool.name],
            "comment": "test",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_validates_tool_names(self):
        """Ensure duplicate and non-existant tool names are rejected."""
        self.client.force_authenticate(user=self.user)
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
        response = self.client.post(url, payload, format="json")
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
        self.client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Update test",
            "tools": [],
            "comment": "unauthenticated update should fail",
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_requires_creator(self):
        """Assert that update requires authentication."""
        new_user = self._user("Testy McTestface")
        self.client.force_authenticate(user=new_user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Update test",
            "tools": [],
            "comment": "non-creator update should fail",
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_update(self):
        """Test update."""
        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Update test",
            "tools": [],
            "comment": "remove a tool from the list",
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.list.id)
        self.assertIn("tools", response.data)
        self.assertEqual(len(response.data["tools"]), 0)

    def test_update_as_oversighter(self):
        """Test update."""
        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        payload = {
            "title": "Oversighter test",
            "tools": [],
            "comment": "remove a tool from the list",
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.list.id)
        self.assertIn("tools", response.data)
        self.assertEqual(len(response.data["tools"]), 0)

    def test_destroy_requires_auth(self):
        """Assert that destroy requires auth."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_destroy_requires_creator(self):
        """Assert that destroy requires list ownership."""
        new_user = self._user("Testy McTestface")
        self.client.force_authenticate(user=new_user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_destroy(self):
        """Test destroy."""
        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_destroy_as_admin(self):
        """Test destroy."""
        self.client.force_authenticate(user=self.administrator)
        url = "/api/lists/{id}/".format(
            id=self.list.pk,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_list(self):
        """Test list."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/"
        response = self.client.get(url)
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
        self.client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.id,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.list.id)
        self.assertIn("tools", response.data)
        self.assertEqual(len(response.data["tools"]), 1)
        self.assertEqual(response.data["tools"][0]["name"], self.tool.name)

    def test_retrieve_ignores_unpublished(self):
        """Ensure that unpublished lists are not shown to non-owners."""
        self.list.published = False
        self.list.save()

        self.client.force_authenticate(user=None)
        url = "/api/lists/{id}/".format(
            id=self.list.id,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_feature_requires_auth(self):
        """Assert that feature fails for anon."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{id}/feature/".format(
            id=self.list.pk,
        )
        payload = {"message": "test feature"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_feature_requires_advanced_rights(self):
        """Assert that feature fails for normal user."""
        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{id}/feature/".format(
            id=self.list.pk,
        )
        payload = {"message": "test feature"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_feature(self):
        """Test marking a list as featured."""
        self.client.force_authenticate(user=self.administrator)
        url = "/api/lists/{id}/feature/".format(
            id=self.list.pk,
        )
        payload = {"message": "test feature"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 204)

    def test_unfeature_requires_auth(self):
        """Assert that unfeature fails for anon."""
        self.list.featured = True
        self.list.save()

        self.client.force_authenticate(user=None)
        url = "/api/lists/{id}/unfeature/".format(
            id=self.list.pk,
        )
        payload = {"message": "test unfeature"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def set_list_featured(self):
        """Set the state of our list to featured."""
        obj = models.ToolList.objects.get(pk=self.list.pk)
        obj.featured = True
        obj.save()

    def test_unfeature_requires_advanced_rights(self):
        """Assert that unfeature fails for normal user."""
        self.set_list_featured()

        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{id}/unfeature/".format(
            id=self.list.pk,
        )
        payload = {"message": "test unfeature"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_unfeature(self):
        """Test marking a list as unfeatured."""
        self.set_list_featured()

        self.client.force_authenticate(user=self.administrator)
        url = "/api/lists/{id}/unfeature/".format(
            id=self.list.pk,
        )
        payload = {"message": "test unfeature"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, 204)


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
        cls.user = cls._user("user")
        cls.oversighter = cls._user("oversighter", group="Oversighters")
        cls.patroller = cls._user("patroller", group="Patrollers")

        cls.toolinfo = cls._load_json("toolinfo_fixture.json")

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
        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/".format(
            list_pk=self.list.pk,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve(self):
        """Test retrieve action."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = self.client.get(url)
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

        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/diff/{other_id}/".format(
            list_pk=self.list.pk,
            id=diff_from,
            other_id=diff_to,
        )
        response = self.client.get(url)
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

        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/diff/{other_id}/".format(
            list_pk=self.list.pk,
            id=diff_from,
            other_id=diff_to,
        )
        response = self.client.get(url)
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

        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/diff/{other_id}/".format(
            list_pk=self.list.pk,
            id=diff_from,
            other_id=diff_to,
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("original", response.data)
        self.assertIn("operations", response.data)
        self.assertIn("result", response.data)
        self.assertTrue(response.data["result"]["suppressed"])

    def test_revert_requires_auth(self):
        """Test revert action."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/revert/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_revert(self):
        """Test revert action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "Changed"
            self.list.save()
        self.assertEqual(self.list.title, "Changed")

        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/revert/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_revert_as_oversighter(self):
        """Test revert action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "Changed"
            self.list.save()
        self.assertEqual(self.list.title, "Changed")

        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/revert/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_requires_auth(self):
        """Test undo action."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/undo/{other_id}/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
            other_id=self.versions().last().pk,
        )
        response = self.client.post(url)
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

        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/undo/{other_id}/".format(
            list_pk=self.list.pk,
            id=undo_from,
            other_id=undo_to,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_as_oversighter(self):
        """Test undo action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "Changed"
            self.list.save()
        self.assertEqual(self.list.title, "Changed")

        undo_from = self.versions().first().pk
        undo_to = self.versions().last().pk
        self.assertNotEqual(undo_from, undo_to)

        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/undo/{other_id}/".format(
            list_pk=self.list.pk,
            id=undo_from,
            other_id=undo_to,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_hide_requires_auth(self):
        """Test hide action."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 401)

    def test_hide_requires_special_rights(self):
        """Test hide action."""
        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_hide_forbids_head(self):
        """Test hide action."""
        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["code"], 4091)

    def test_hide(self):
        """Test hide action."""
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.list.title = "REVERTED"
            self.list.save()

        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/hide/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)
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

        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)
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

        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=bad_faith.pk,
        )
        response = self.client.patch(url)
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

        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=bad_faith.pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 204)

    def test_reveal_rejects_unhidden(self):
        """Test reveal action."""
        self.client.force_authenticate(user=self.oversighter)
        url = "/api/lists/{list_pk}/revisions/{id}/reveal/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 404)

    def test_patrol_requires_auth(self):
        """Test patrol action."""
        self.client.force_authenticate(user=None)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 401)

    def test_patrol_requires_special_rights(self):
        """Test patrol action."""
        self.client.force_authenticate(user=self.user)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 403)

    def test_patrol(self):
        """Test patrol action."""
        self.client.force_authenticate(user=self.patroller)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 204)

    def test_patrol_rejects_patrolled(self):
        """Test patrol action."""
        p = self.versions().first()
        p.revision.meta.patrolled = True
        p.revision.meta.save()

        self.client.force_authenticate(user=self.patroller)
        url = "/api/lists/{list_pk}/revisions/{id}/patrol/".format(
            list_pk=self.list.pk,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 400)


class FavoritesViewSetTest(TestCase):
    """Test FavoritesViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")

        cls.toolinfo = cls._load_json("toolinfo_fixture.json")

        cls.tool, _, _ = Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, Tool.ORIGIN_API
        )

    def test_list_requires_auth(self):
        """Assert that anons get a 401 when calling."""
        self.client.force_authenticate(user=None)
        url = "/api/user/favorites/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_list(self):
        """Test list action."""
        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 0)

    def test_create_requires_auth(self):
        """Assert that anons get a 401 when calling."""
        self.client.force_authenticate(user=None)
        url = "/api/user/favorites/"
        payload = {
            "name": self.tool.name,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create action."""
        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/"
        payload = {
            "name": self.tool.name,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.tool.name)

    def test_create_rejects_duplicates(self):
        """Test create action."""
        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/"
        payload = {
            "name": self.tool.name,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.data)
        self.assertEqual("name", response.data["errors"][0]["field"])

    def test_retrieve_requires_auth(self):
        """Assert that anons get a 401 when calling."""
        self.client.force_authenticate(user=None)
        url = "/api/user/favorites/{name}/".format(
            name=self.tool.name,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_retrieve_404(self):
        """Assert that a 404 is returned when a tool is not on the list."""
        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/{name}/".format(
            name=self.tool.name,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_retrieve(self):
        """Test retrieve action."""
        toollist = models.ToolListItem.objects.get_user_favorites(self.user)
        item = models.ToolListItem.objects.create(
            toollist=toollist,
            tool=self.tool,
            order=0,
            added_by=self.user,
        )
        self.assertEqual(item.toollist, toollist)
        self.assertEqual(item.tool, self.tool)

        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/{name}/".format(
            name=self.tool.name,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.tool.name)

    def test_delete_requires_auth(self):
        """Assert that anons get a 401 when calling."""
        self.client.force_authenticate(user=None)
        url = "/api/user/favorites/{name}/".format(
            name=self.tool.name,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_delete_404(self):
        """Assert that a 404 is returned when a tool is not on the list."""
        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/{name}/".format(
            name=self.tool.name,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        """Test the delete action."""
        toollist = models.ToolListItem.objects.get_user_favorites(self.user)
        item = models.ToolListItem.objects.create(
            toollist=toollist,
            tool=self.tool,
            order=0,
            added_by=self.user,
        )
        self.assertEqual(item.toollist, toollist)
        self.assertEqual(item.tool, self.tool)

        self.client.force_authenticate(user=self.user)
        url = "/api/user/favorites/{name}/".format(
            name=self.tool.name,
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
