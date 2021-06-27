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

from toolhub.apps.toolinfo.serializers import SummaryToolSerializer
from toolhub.apps.toolinfo.serializers import ToolSerializer
from toolhub.apps.user.serializers import UserSerializer
from toolhub.decorators import doc
from toolhub.serializers import ModelSerializer

from .models import ToolList


@doc(_("""List of tools metadata."""))
class ToolListSerializer(ModelSerializer):
    """List of tools."""

    created_by = UserSerializer(many=False)
    modified_by = UserSerializer(many=False)
    tools = SummaryToolSerializer(many=True)

    class Meta:
        """Configure serializer."""

        model = ToolList
        fields = [
            "id",
            "title",
            "description",
            "icon",
            "favorites",
            "published",
            "featured",
            "tools",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ]
        read_only_fields = [
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ]


@doc(_("""List of tools with details."""))
class ToolListDetailSerializer(ToolListSerializer):
    """List of tools with details."""

    tools = ToolSerializer(many=True)

    class Meta(ToolListSerializer.Meta):
        """Configure serializer."""
