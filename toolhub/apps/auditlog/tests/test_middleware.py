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
from unittest.mock import Mock

from django.test import SimpleTestCase

from ..context import threadlocal
from ..middleware import LogEntryUserMiddleware


class LogEntryUserMiddlewareTest(SimpleTestCase):
    """Test middleware."""

    def setUp(self):
        """Initialize common test conditions."""
        self.get_response = Mock()
        self.middleware = LogEntryUserMiddleware(self.get_response)
        self.request = Mock()
        self.request.user = Mock()

    def test_anon_user(self):
        """Assert that nullcontext is used with anon request."""
        self.request.user.is_authenticated = False

        def assert_null_context(req):
            self.assertEqual(getattr(threadlocal, "auditlog", None), None)
            return req

        self.get_response.side_effect = assert_null_context

        self.assertEqual(
            getattr(threadlocal, "auditlog", None),
            None,
            msg="No threadlocal value before middleware.",
        )

        self.middleware(self.request)

        self.get_response.assert_called_once()

    def test_authed_user(self):
        """Assert that authed request sets auditlog hook."""
        self.request.user.is_authenticated = True

        def assert_thread_local(req):
            self.assertIsInstance(getattr(threadlocal, "auditlog", None), dict)
            self.assertIn("dispatch_uid", threadlocal.auditlog)
            self.assertIsInstance(threadlocal.auditlog["dispatch_uid"], tuple)
            return req

        self.get_response.side_effect = assert_thread_local

        self.assertEqual(
            getattr(threadlocal, "auditlog", None),
            None,
            msg="No threadlocal value before middleware.",
        )

        self.middleware(self.request)

        self.get_response.assert_called_once()
        self.assertEqual(
            getattr(threadlocal, "auditlog", None),
            None,
            msg="No threadlocal value after middleware.",
        )
