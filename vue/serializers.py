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
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from toolhub.decorators import doc
from toolhub.serializers import Serializer


@doc(_("""Information used on the Toolhub Home view."""))
class HomeSerializer(Serializer):
    """Information used on the Toolhub Home view."""

    total_tools = serializers.IntegerField(
        read_only=True,
        help_text=_("Count of tools known to Toolhub."),
    )
    last_crawl_time = serializers.DateTimeField(
        read_only=True,
        help_text=_("Date and time of most recent crawler run."),
    )
    last_crawl_changed = serializers.IntegerField(
        read_only=True,
        help_text=_(
            "Number of tools added or updated in the most recent "
            "crawler run."
        ),
    )

    def create(self, validated_data):
        """Operation not implemented."""
        raise NotImplementedError("Data output only serializer.")

    def update(self, instance, validated_data):
        """Operation not implemented."""
        raise NotImplementedError("Data output only serializer.")
