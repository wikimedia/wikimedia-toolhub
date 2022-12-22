# Copyright (c) 2022 Wikimedia Foundation and contributors.
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
from django.test import SimpleTestCase

from ..spdx import SPDX_LICENSES


class SPDXTest(SimpleTestCase):
    """Test SPDX structure."""

    def test_dictKeys(self):
        """Assert the dict is keyed by licenseId value."""
        for key, val in SPDX_LICENSES.items():
            self.assertEqual(key, val["licenseId"])

    def test_bool_values(self):
        """Assert type of boolean fields."""
        for entry in SPDX_LICENSES.values():
            self.assertEqual(type(entry["isFsfLibre"]), bool)
            self.assertEqual(type(entry["isOsiApproved"]), bool)
            self.assertEqual(type(entry["isDeprecatedLicenseId"]), bool)

    def test_string_values(self):
        """Assert type of string fields."""
        for entry in SPDX_LICENSES.values():
            self.assertEqual(type(entry["licenseId"]), str)
            self.assertEqual(type(entry["name"]), str)

    def test_int_values(self):
        """Assert type of int fields."""
        for entry in SPDX_LICENSES.values():
            self.assertEqual(type(entry["referenceNumber"]), int)

    def test_referenceNumber_unique(self):
        """Assert that each referenceNumber is unique."""
        seen = set()
        for entry in SPDX_LICENSES.values():
            self.assertNotIn(entry["referenceNumber"], seen)
            seen.add(entry["referenceNumber"])

    def test_name_unique(self):
        """Assert that each name is unique."""
        seen = set()
        for entry in SPDX_LICENSES.values():
            if entry["isDeprecatedLicenseId"]:
                continue
            self.assertNotIn(entry["name"], seen)
            seen.add(entry["name"])
