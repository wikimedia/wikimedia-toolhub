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
        cls.crat = ToolhubUser.objects.create_user(  # nosec: B106
            username="Bureaucrat",
            email="crat@example.org",
            password="unused",
        )
        Group.objects.get(name="Bureaucrats").user_set.add(cls.crat)
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

    def test_anon(self):
        """Anon user should get boring permissions."""
        rules = permissions.casl_for_user(self.anon)
        self.assertEqual(rules, [])

    def test_user(self):
        """A user with no groups should be able to edit their objects."""
        rules = permissions.casl_for_user(self.user)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            action = rule["action"]
            self.assertIn(action, ["add", "change", "delete"])
            if action in ["change", "delete"]:
                self.assertIn("conditions", rule)
                conds = rule["conditions"]
                self.assertTrue(len(conds) > 0)
                if "origin" in conds:
                    self.assertEqual(rule["subject"], "toolinfo/tool")
                    self.assertEqual(conds["origin"], "api")
                    conds.pop("origin")
                self.assertEqual(len(conds), 1)
                # The name of the condition varies by predicate, but it will
                # always check for a value == the user's id
                self.assertEqual(conds.popitem()[1], self.user.id)

    def test_admin(self):
        """An Administrator can do it all."""
        rules = permissions.casl_for_user(self.admin)
        for rule in rules:
            self.assertIn("subject", rule)
            self.assertIn("action", rule)
            action = rule["action"]
            self.assertIn(action, ["add", "change", "delete"])
            if rule["subject"] == "toolinfo/tool" and action != "add":
                self.assertIn("conditions", rule)
                conds = rule["conditions"]
                self.assertEqual(conds["origin"], "api")
                conds.pop("origin")
                self.assertEqual(len(conds), 0)
            else:
                self.assertNotIn("conditions", rule)

    # TODO: add tests for oversighter and patroller once they have some
    # special roles in the system
