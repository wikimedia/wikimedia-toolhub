# Copyright (c) 2020 Wikimedia Foundation and contributors.
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
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from toolhub.apps.user.models import ToolhubUser

from ..models import LogEntry


class LogEntryTest(TestCase):
    """Test LogEntry and LogEntryManager."""

    def setUp(self):
        """Initialize common test conditions."""
        self.user = ToolhubUser.objects.create(
            username="tester",
            email="tester@example.org",
        )

    def test_log_entry_manager(self):
        """Make a LogEntry via LogEntryManager."""
        obj = LogEntry.objects.log_action(
            user=self.user,
            target=self.user,
            action=LogEntry.UPDATE,
            msg="test_log_entry_manager_log_action",
        )
        self.assertIsInstance(obj, LogEntry)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(
            obj.content_type,
            ContentType.objects.get_for_model(ToolhubUser),
        )
        self.assertEqual(obj.object_id, self.user.id)
        self.assertEqual(obj.object_pk, None)
        self.assertEqual(obj.action, LogEntry.UPDATE)
        self.assertEqual(
            obj.change_message,
            "test_log_entry_manager_log_action",
        )
        self.assertEqual(obj.get_target(), self.user)

        qs = LogEntry.objects.get_for_object(self.user)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.last(), obj)
