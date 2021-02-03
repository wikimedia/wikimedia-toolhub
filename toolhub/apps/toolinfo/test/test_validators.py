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
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from ..validators import validate_spdx


class ValidatorsTest(SimpleTestCase):
    """Test validators."""

    def test_validate_spdx_valid(self):
        """Valid SPDX id are valid."""
        validate_spdx("0BSD")
        validate_spdx("GPL-3.0-or-later")
        validate_spdx("AGPL-3.0-or-later")
        validate_spdx("CC-BY-SA-4.0")

    def test_validate_spdx_invalid(self):
        """Invalid SPDX id are invalid."""
        with self.assertRaises(ValidationError):
            validate_spdx("")
        with self.assertRaises(ValidationError):
            validate_spdx(None)
        with self.assertRaises(ValidationError):
            validate_spdx("bd808-general-license")
