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

from toolhub.apps.versioned.models import RevisionMetadata
from toolhub.tests import TestCase

from .. import models


class ToolViewSetTest(TestCase):
    """Test ToolViewSet."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")
        cls.administrator = cls._user("admin", group="Administrators")
        cls.toolinfo = cls._load_json("toolinfo_fixture.json")
        cls.fixture = cls._load_json("view_fixture.json")

        cls.tool, _, _ = models.Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, models.Tool.ORIGIN_API
        )

    def test_create_requires_auth(self):
        """Assert that create fails for anon."""
        self.client.force_authenticate(user=None)

        response = self.client.post("/api/tools/", self.fixture, format="json")

        self.assertEqual(response.status_code, 401)

    def test_create(self):
        """Test create."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/tools/", self.fixture, format="json")

        self.assertEqual(response.status_code, 201)

    def test_retrieve(self):
        """Test retrieve."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/{name}/".format(name=self.tool.name)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["name"], self.tool.name)

    def test_update_requires_auth(self):
        """Assert that update requires authentication."""
        self.client.force_authenticate(user=None)
        self.fixture["description"] = "test_update_requires_auth"
        self.fixture["comment"] = "test_update_requires_auth"

        url = "/api/tools/{name}/".format(name=self.tool.name)
        response = self.client.put(url, self.fixture, format="json")

        self.assertEqual(response.status_code, 401)

    def test_update(self):
        """Test update."""
        self.client.force_authenticate(user=self.user)
        self.fixture["description"] = "test_update"
        self.fixture["comment"] = "test_update"

        url = "/api/tools/{name}/".format(name=self.tool.name)
        response = self.client.put(url, self.fixture, format="json")

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["name"], self.tool.name)
        self.assertEqual(data["description"], self.fixture["description"])

    def test_destroy_requires_auth(self):
        """Assert that destroy requires auth."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/{name}/".format(name=self.tool.name)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)

    def test_destroy(self):
        """Test destroy."""
        self.client.force_authenticate(user=self.user)

        url = "/api/tools/{name}/".format(name=self.tool.name)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_destroy_as_admin(self):
        """Administrators should be able to delete anything."""
        self.client.force_authenticate(user=self.administrator)

        url = "/api/tools/{name}/".format(name=self.tool.name)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_list(self):
        """Test list."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        tool = response.data["results"][0]
        self.assertIn("name", tool)
        self.assertEqual(tool["name"], self.tool.name)


class ToolRevisionViewSetTest(TestCase):
    """Test ToolRevisionViewSet."""

    @classmethod
    def versions(cls, tool=None):
        """Get queryset over versions."""
        if tool is None:
            tool = cls.tool
        return Version.objects.get_for_object(tool)

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.user = cls._user("user")
        cls.administrator = cls._user("admin", group="Administrators")
        cls.oversighter = cls._user("oversighter", group="Oversighters")
        cls.patroller = cls._user("patroller", group="Patrollers")

        cls.toolinfo = cls._load_json("toolinfo_fixture.json")

        cls.tool, _, _ = models.Tool.objects.from_toolinfo(
            cls.toolinfo, cls.user, models.Tool.ORIGIN_API
        )

    def test_list(self):
        """Test list action."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/{name}/revisions/".format(name=self.tool.name)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve(self):
        """Test retrieve action."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/{name}/revisions/{id}/".format(
            name=self.tool.name,
            id=self.versions().first().pk,
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_diff(self):
        """Test diff action."""
        self.client.force_authenticate(user=None)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "Changed"
            self.tool.save()
        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk

        url = "/api/tools/{name}/revisions/{id}/diff/{other_id}/".format(
            name=self.tool.name,
            id=diff_from,
            other_id=diff_to,
        )
        response = self.client.get(url)

        self.assertNotEqual(diff_from, diff_to)
        self.assertEqual(response.status_code, 200)
        self.assertIn("original", response.data)
        self.assertIn("operations", response.data)
        self.assertIn("result", response.data)

    def test_diff_suppressed_anon(self):
        """Test diff with suppressed start/end as anon."""
        self.client.force_authenticate(user=None)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "BAD FAITH"
            self.tool.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()
        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk

        url = "/api/tools/{name}/revisions/{id}/diff/{other_id}/".format(
            name=self.tool.name,
            id=diff_from,
            other_id=diff_to,
        )
        response = self.client.get(url)

        self.assertTrue(self.versions().last().revision.meta.suppressed)
        self.assertNotEqual(diff_from, diff_to)
        self.assertEqual(response.status_code, 403)

    def test_diff_suppressed_priv(self):
        """Test diff with suppressed start/end as privledged user."""
        self.client.force_authenticate(user=self.oversighter)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "BAD FAITH"
            self.tool.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()
        diff_from = self.versions().first().pk
        diff_to = self.versions().last().pk

        url = "/api/tools/{name}/revisions/{id}/diff/{other_id}/".format(
            name=self.tool.name,
            id=diff_from,
            other_id=diff_to,
        )
        response = self.client.get(url)

        self.assertTrue(self.versions().last().revision.meta.suppressed)
        self.assertNotEqual(diff_from, diff_to)
        self.assertEqual(response.status_code, 200)
        self.assertIn("original", response.data)
        self.assertIn("operations", response.data)
        self.assertIn("result", response.data)
        self.assertTrue(response.data["result"]["suppressed"])

    def test_revert_requires_auth(self):
        """Test revert action."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/{name}/revisions/{id}/revert/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_revert(self):
        """Test revert action."""
        self.client.force_authenticate(user=self.user)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "Changed"
            self.tool.save()

        url = "/api/tools/{name}/revisions/{id}/revert/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.post(url)

        self.assertEqual(self.tool.title, "Changed")
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_revert_as_oversighter(self):
        """Oversighters can revert any edit."""
        self.client.force_authenticate(user=self.oversighter)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "Changed"
            self.tool.save()

        url = "/api/tools/{name}/revisions/{id}/revert/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.post(url)

        self.assertEqual(self.tool.title, "Changed")
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_requires_auth(self):
        """Test undo action."""
        self.client.force_authenticate(user=None)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "Changed"
            self.tool.save()
        undo_from = self.versions().first().pk
        undo_to = self.versions().last().pk

        url = "/api/tools/{name}/revisions/{id}/undo/{other_id}/".format(
            name=self.tool.name,
            id=undo_from,
            other_id=undo_to,
        )
        response = self.client.post(url)

        self.assertEqual(self.tool.title, "Changed")
        self.assertNotEqual(undo_from, undo_to)
        self.assertEqual(response.status_code, 401)

    def test_undo(self):
        """Test undo action."""
        self.client.force_authenticate(user=self.user)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "Changed"
            self.tool.save()
        undo_from = self.versions().first().pk
        undo_to = self.versions().last().pk

        url = "/api/tools/{name}/revisions/{id}/undo/{other_id}/".format(
            name=self.tool.name,
            id=undo_from,
            other_id=undo_to,
        )
        response = self.client.post(url)

        self.assertEqual(self.tool.title, "Changed")
        self.assertNotEqual(undo_from, undo_to)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_as_oversighter(self):
        """Oversighters should be able to undo anything."""
        self.client.force_authenticate(user=self.oversighter)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "Changed"
            self.tool.save()
        undo_from = self.versions().first().pk
        undo_to = self.versions().last().pk

        url = "/api/tools/{name}/revisions/{id}/undo/{other_id}/".format(
            name=self.tool.name,
            id=undo_from,
            other_id=undo_to,
        )
        response = self.client.post(url)

        self.assertEqual(self.tool.title, "Changed")
        self.assertNotEqual(undo_from, undo_to)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.data)
        self.assertNotEqual(response.data["title"], "Changed")

    def test_undo_invalid(self):
        """Test undo action."""
        self.client.force_authenticate(user=self.user)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.technology_used = []
            self.tool.save()
        # Prepare an undo that tries to empty an already empty array
        undo_from = self.versions().last().pk
        undo_to = self.versions().first().pk

        url = "/api/tools/{name}/revisions/{id}/undo/{other_id}/".format(
            name=self.tool.name,
            id=undo_from,
            other_id=undo_to,
        )
        response = self.client.post(url)

        self.assertEqual(self.tool.technology_used, [])
        self.assertNotEqual(undo_from, undo_to)
        self.assertEqual(response.status_code, 409)

    def test_hide_requires_auth(self):
        """Test hide action."""
        self.client.force_authenticate(user=None)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "REVERTED"
            self.tool.save()

        url = "/api/tools/{name}/revisions/{id}/hide/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 401)

    def test_hide_requires_special_rights(self):
        """Test hide action."""
        self.client.force_authenticate(user=self.user)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "REVERTED"
            self.tool.save()

        url = "/api/tools/{name}/revisions/{id}/hide/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["code"], 4005)

    def test_hide(self):
        """Test hide action."""
        self.client.force_authenticate(user=self.oversighter)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "REVERTED"
            self.tool.save()

        url = "/api/tools/{name}/revisions/{id}/hide/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.versions()[1].revision.meta.suppressed)

    def test_hide_forbids_head(self):
        """Test hide action."""
        self.client.force_authenticate(user=self.oversighter)

        url = "/api/tools/{name}/revisions/{id}/hide/".format(
            name=self.tool.name,
            id=self.versions().last().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["code"], 4091)

    def test_reveal_requires_auth(self):
        """Test reveal action."""
        self.client.force_authenticate(user=None)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "REVERTED"
            self.tool.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        url = "/api/tools/{name}/revisions/{id}/reveal/".format(
            name=self.tool.name,
            id=bad_faith.pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 401)

    def test_reveal_requires_special_rights(self):
        """Test reveal action."""
        self.client.force_authenticate(user=self.user)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "REVERTED"
            self.tool.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        url = "/api/tools/{name}/revisions/{id}/reveal/".format(
            name=self.tool.name,
            id=bad_faith.pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 403)

    def test_reveal(self):
        """Test reveal action."""
        self.client.force_authenticate(user=self.oversighter)
        with reversion.create_revision():
            reversion.add_meta(RevisionMetadata)
            self.tool.title = "REVERTED"
            self.tool.save()
        bad_faith = self.versions().last()
        bad_faith.revision.meta.suppressed = True
        bad_faith.revision.meta.save()

        url = "/api/tools/{name}/revisions/{id}/reveal/".format(
            name=self.tool.name,
            id=bad_faith.pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 204)

    def test_reveal_rejects_unhidden(self):
        """Test reveal action."""
        self.client.force_authenticate(user=self.oversighter)

        url = "/api/tools/{name}/revisions/{id}/reveal/".format(
            name=self.tool.name,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 404)

    def test_patrol_requires_auth(self):
        """Test patrol action."""
        self.client.force_authenticate(user=None)

        url = "/api/tools/{tool_name}/revisions/{id}/patrol/".format(
            tool_name=self.tool.name,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 401)

    def test_patrol_requires_special_rights(self):
        """Test patrol action."""
        self.client.force_authenticate(user=self.user)

        url = "/api/tools/{tool_name}/revisions/{id}/patrol/".format(
            tool_name=self.tool.name,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 403)

    def test_patrol(self):
        """Test patrol action."""
        self.client.force_authenticate(user=self.patroller)

        url = "/api/tools/{tool_name}/revisions/{id}/patrol/".format(
            tool_name=self.tool.name,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 204)

    def test_patrol_rejects_patrolled(self):
        """Test patrol action."""
        self.client.force_authenticate(user=self.patroller)
        p = self.versions().first()
        p.revision.meta.patrolled = True
        p.revision.meta.save()

        url = "/api/tools/{tool_name}/revisions/{id}/patrol/".format(
            tool_name=self.tool.name,
            id=self.versions().first().pk,
        )
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 404)
