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

from toolhub.apps.user.models import ToolhubUser

from .. import permissions


class CASLForUserTest(TestCase):
    """Test casl_for_user."""

    @classmethod
    def setUpTestData(cls):
        """Setup for all tests in this TestCase."""
        cls.anon = AnonymousUser()
        cls.user = ToolhubUser.objects.create_user(  # nosec: B106
            username="Demo Unicorn",
            email="bdavis+dunicorn@wikimedia.org",
            password="unused",
        )
        cls.admin = ToolhubUser.objects.create_user(  # nosec: B106
            username="Admin",
            email="admin@example.org",
            password="unused",
        )
        Group.objects.get(name="Administrators").user_set.add(cls.admin)
        cls.bureaucrat = ToolhubUser.objects.create_user(  # nosec: B106
            username="Bureaucrat",
            email="crat@example.org",
            password="unused",
        )
        Group.objects.get(name="Bureaucrats").user_set.add(cls.bureaucrat)
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

    def assertRuleViewUnsuppressed(self, rule):
        """Assert that the rule allows viewing if suppressed=False."""
        self.assertEqual(rule["subject"], "reversion/version")
        self.assertEqual(rule["action"], "view")
        self.assertIn("conditions", rule)
        conds = rule["conditions"]
        self.assertEqual(len(conds), 1)
        self.assertEqual(conds["suppressed"], False)

    def assertRuleChangeDelete(self, rule, user_id):
        """Assert that the rule allows based on user id."""
        self.assertIn(rule["action"], ["change", "delete"])
        self.assertIn("conditions", rule)
        conds = rule["conditions"]
        self.assertTrue(len(conds) > 0)
        if "origin" in conds:
            # All toolinfo edit/delete actions are restricted to orgin=api
            self.assertEqual(rule["subject"], "toolinfo/tool")
            self.assertEqual(conds["origin"], "api")
            conds.pop("origin")
        self.assertEqual(len(conds), 1)
        # The name of the condition varies by predicate, but it will
        # always check for a value == the user's id
        self.assertEqual(conds.popitem()[1], user_id)

    def test_anon(self):
        """Anon user should get boring permissions."""
        rules = permissions.casl_for_user(self.anon)
        for rule in rules:
            self.assertEqual(rule["action"], "view")

    def test_user(self):
        """A user with no groups should be able to edit their objects."""
        rules = permissions.casl_for_user(self.user)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            subject = rule["subject"]
            action = rule["action"]
            self.assertIn(action, ["view", "add", "change", "delete"])
            if action == "view" and subject == "reversion/version":
                self.assertRuleViewUnsuppressed(rule)
            elif action in ["change", "delete"]:
                self.assertRuleChangeDelete(rule, self.user.id)

    def test_admin(self):
        """An Administrator can do it all."""
        rules = permissions.casl_for_user(self.admin)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            subject = rule["subject"]
            action = rule["action"]
            self.assertIn(
                action,
                ["view", "add", "change", "delete", "patrol", "feature"],
            )
            if subject == "toolinfo/tool" and action in ["change", "delete"]:
                # Even admins cannot edit non-api origin toolinfo records
                self.assertIn("conditions", rule)
                conds = rule["conditions"]
                self.assertEqual(conds["origin"], "api")
                conds.pop("origin")
                self.assertEqual(len(conds), 0)
            else:
                self.assertNotIn("conditions", rule)

    def test_bureaucrat(self):
        """Verify bureaucrat perms."""
        rules = permissions.casl_for_user(self.bureaucrat)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            subject = rule["subject"]
            action = rule["action"]
            self.assertIn(action, ["view", "add", "change", "delete"])
            if action == "view" and subject == "reversion/version":
                self.assertRuleViewUnsuppressed(rule)
            elif action in ["change", "delete"]:
                if subject == "auth/group":
                    # Bureaucrats get unconditional ability to edit groups
                    self.assertNotIn("conditions", rule)
                else:
                    self.assertRuleChangeDelete(rule, self.bureaucrat.id)

    def test_oversighter(self):
        """Verify oversighter perms."""
        rules = permissions.casl_for_user(self.oversighter)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            subject = rule["subject"]
            action = rule["action"]
            self.assertIn(action, ["view", "add", "change", "delete"])
            if action == "view" and subject == "reversion/version":
                # Oversighters get unconditional ability to view
                # reversion/version instances.
                self.assertNotIn("conditions", rule)
            elif action == "change":
                if subject in (
                    "lists/toollist",
                    "reversion/version",
                ):
                    # Oversighters get unconditional ability to change user
                    # created content so that they can remove harmful content
                    # before supressing.
                    self.assertNotIn("conditions", rule)

                elif subject == "toolinfo/tool":
                    # Even oversighters cannot edit non-api origin toolinfo
                    # records
                    self.assertIn("conditions", rule)
                    conds = rule["conditions"]
                    self.assertEqual(conds["origin"], "api")
                    conds.pop("origin")
                    self.assertEqual(len(conds), 0)

                else:
                    self.assertRuleChangeDelete(rule, self.oversighter.id)
            elif action == "delete":
                self.assertRuleChangeDelete(rule, self.oversighter.id)

    def test_patroller(self):
        """Verify patroller perms."""
        rules = permissions.casl_for_user(self.patroller)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            subject = rule["subject"]
            action = rule["action"]
            self.assertIn(
                action, ["view", "add", "change", "delete", "patrol"]
            )
            if action == "view" and subject == "reversion/version":
                self.assertRuleViewUnsuppressed(rule)
            elif action in ["change", "delete"]:
                self.assertRuleChangeDelete(rule, self.patroller.id)
            elif action == "patrol":
                self.assertEqual(subject, "reversion/version")
                self.assertNotIn("conditions", rule)
