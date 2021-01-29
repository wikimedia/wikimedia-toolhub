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
from django.test import TestCase

from toolhub.apps.user.models import ToolhubUser

from ..context import auditlog_context
from ..context import threadlocal


class ContextTest(TestCase):
    """Test contextmanagers."""

    def setUp(self):
        """Initialize common test conditions."""
        self.user = ToolhubUser.objects.create(
            username="tester",
            email="tester@example.org",
        )

    def test_auditlog_context(self):
        """Assert threadlocal state while using."""
        self.assertEqual(
            getattr(threadlocal, "auditlog", None),
            None,
            msg="No threadlocal value before contextmanager.",
        )
        with auditlog_context(self.user, "some comment"):
            self.assertIsInstance(getattr(threadlocal, "auditlog", None), dict)
            self.assertIn("dispatch_uid", threadlocal.auditlog)
            self.assertIsInstance(threadlocal.auditlog["dispatch_uid"], tuple)
        self.assertEqual(
            getattr(threadlocal, "auditlog", None),
            None,
            msg="No threadlocal value after contextmanager.",
        )
