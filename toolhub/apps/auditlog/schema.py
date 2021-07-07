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


PARAMS = {
    "description": _("Event parameters"),
    "type": "object",
    "properties": {
        "revision": {
            "description": _("Revision created by edit action"),
            "type": "integer",
            "required": False,
        },
        "suppressed": {
            "description": _("Has the revision been marked as hidden?"),
            "type": "boolean",
            "required": False,
        },
        "patrolled": {
            "description": _("Has the revision been reviewed by a patroller?"),
            "type": "boolean",
            "required": False,
        },
        "tool_name": {
            "description": _("Name of tool related to the change"),
            "type": "string",
            "required": False,
        },
        "user": {
            "description": _("Identity of user related to the change"),
            "type": "object",
            "required": False,
            "properties": {
                "id": {
                    "type": "integer",
                },
                "username": {
                    "type": "string",
                },
            },
        },
        "toollist": {
            "description": _("Tool list related to the change"),
            "type": "object",
            "required": False,
            "properties": {
                "id": {
                    "type": "integer",
                },
                "title": {
                    "type": "string",
                },
            },
        },
    },
}
