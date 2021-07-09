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
from django import shortcuts
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema

from rest_framework.response import Response
from rest_framework.views import APIView

from toolhub.apps.crawler.models import Run
from toolhub.apps.toolinfo.models import Tool

from .serializers import HomeSerializer


def main(request, **kwargs):  # noqa: W0613
    """Serve a page embedding the Vue frontend's main component."""
    return shortcuts.render(request, "vue/main.html")


class HomeView(APIView):
    """Basic info for use on the Home screen."""

    @extend_schema(
        description=_("""Get information used on the Toolhub Home view."""),
        responses=HomeSerializer,
    )
    def get(self, request):
        """Get info."""
        last_run = (
            Run.objects.exclude(end_date__isnull=True)
            .order_by("-end_date")
            .first()
        )
        info = {
            "total_tools": Tool.objects.all().count(),
            "last_crawl_time": last_run.end_date,
            "last_crawl_changed": last_run.new_tools + last_run.updated_tools,
        }
        serializer = HomeSerializer(info)
        return Response(serializer.data)
