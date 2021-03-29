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
import logging

from django.test import SimpleTestCase

from ..logging import LogCaptureContext


class LogCaptureContextTest(SimpleTestCase):
    """Test LogCaptureContext."""

    def test_capture(self):
        """Assert logs are captured."""
        logger = logging.getLogger("test_capture")
        logger.setLevel(logging.DEBUG)
        logs = None
        logger.info("1. should not be captured")
        with LogCaptureContext(level=logging.INFO) as ctx:
            logger.debug("2. should not be captured")
            logger.info("3. should be captured")
            logging.warning("4. should be captured")
            logs = ctx.getvalue()
        log_lines = logs.splitlines()
        self.assertEqual(2, len(log_lines))
        self.assertIn("3. should be captured", log_lines[0])
        self.assertIn("4. should be captured", log_lines[1])
