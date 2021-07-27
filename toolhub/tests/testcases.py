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
import contextlib
import json
import os
import sys

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.text import slugify

from rest_framework.test import APITestCase


class TestCase(APITestCase):
    """Atomic transactional API test base."""

    @classmethod
    def _user(cls, username, group=None):
        """Make a user account with optional group membership."""
        user = get_user_model().objects.create_user(  # nosec: B106
            username=username,
            email="{}@example.org".format(slugify(username)),
            password="unused",
        )
        if group:
            Group.objects.get(name=group).user_set.add(user)
        return user

    @classmethod
    def _class_dir(cls):
        """Get the filesystem directory containing this class."""
        return os.path.dirname(
            os.path.abspath(sys.modules[cls.__module__].__file__)
        )

    @classmethod
    @contextlib.contextmanager
    def _open(cls, filename):
        """Contextmanager for openting a file relative to the class."""
        with open(os.path.join(cls._class_dir(), filename)) as fhandle:
            yield fhandle

    @classmethod
    def _load_json(cls, filename):
        """Load a json file relatvie to the class."""
        with cls._open(filename) as fh:
            return json.load(fh)
