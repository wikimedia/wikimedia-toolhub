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
from django.contrib.auth import get_user_model
from django.test import TestCase

from toolhub.apps.toolinfo.models import Tool

from ..models import Run
from ..models import RunUrl
from ..models import Url


class UrlTestCase(TestCase):
    """Url tests."""

    def test_str(self):
        """A Url's string representation is the url."""
        user = get_user_model().objects.create_user("testing")
        url = Url.objects.create(
            url="https://example.org/toolinfo.json",
            created_by=user,
        )
        self.assertEqual(str(url), url.url)

    def test_url_delete(self):
        """Verify that deleting a url also deletes related tools"""
        tool_name = "test-tool"

        user = get_user_model().objects.create_user("testing")

        url = Url.objects.create(
            url="https://example.org/toolinfo.json",
            created_by=user,
        )

        run = Run.objects.create()

        tool = Tool.objects.create(
            name=tool_name,
            title="test tool",
            description="test tool",
            url="https://test-tool.org",
            created_by=user,
        )

        runUrl = RunUrl(run=run, url=url, status_code=200)
        runUrl.save()
        runUrl.tools.add(tool)

        url.delete()
        tool = Tool.objects.filter(name=tool_name)
        self.assertEqual(len(tool), 0)
