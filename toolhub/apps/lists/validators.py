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
import collections

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from toolhub.apps.toolinfo.models import Tool

from .models import ToolListItem


def validate_unique_list(value):
    """Ensure that the given list has no duplicates."""
    names = set(value)
    if len(names) != len(value):
        dups = collections.Counter(value) - collections.Counter(names)
        dups = list(dups.keys())
        raise ValidationError(
            _("Duplicate values in list: %(duplicates)s"),
            code="duplicate_values",
            params={"duplicates": ", ".join(dups)},
        )


def validate_tools_exist(value):
    """Ensure that the provided data is a list of current tool names."""
    if type(value) is str:
        value = [value]
    names = set(value)
    found = {
        tool["name"]
        for tool in Tool.objects.filter(name__in=names).values("name")
    }
    if len(found) != len(names):
        bad = names.difference(found)
        raise ValidationError(
            ngettext_lazy(
                "Unknown tool: %(names)s",
                "Unknown tools: %(names)s",
                len(bad),
            ),
            code="unknown_tool",
            params={"names": ", ".join(bad)},
        )


def validate_favorites_unique(name, ctx):
    """Ensure that the provided data is not already a favorite tool."""
    user = ctx.context["request"].user
    favorites = ToolListItem.objects.get_user_favorites(user)
    try:
        ToolListItem.objects.get(toollist=favorites, tool__name=name)
    except ToolListItem.DoesNotExist:
        # Happy path
        return
    raise ValidationError(
        _("""Tool %(name)s is already favorited."""),
        code="duplicate_favorite",
        params={"name": name},
    )


# Mark validate_favorites_unique as needing context to be passed by the caller
validate_favorites_unique.requires_context = True
