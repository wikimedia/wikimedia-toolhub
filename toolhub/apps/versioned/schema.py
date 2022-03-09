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

CONTENT_ID = {
    "description": _("unique identifier of the content being versioned"),
    "type": "string",
}

CONTENT_TITLE = {
    "description": _("title describing the content being versioned"),
    "type": "string",
}

JSONPATCH = {
    "description": _("RFC 6902 application/json-patch+json data"),
    "type": "array",
    "items": {
        "description": _("RFC 6902 JSON patch operation"),
        "type": "object",
        "required": ["op", "path"],
        "properties": {
            "op": {
                "description": _("The operation to be performed"),
                "type": "string",
                "enum": ["add", "remove", "replace", "move", "copy", "test"],
            },
            "path": {
                "description": _(
                    "JSON-Pointer to location within document "
                    "where operation is performed."
                ),
                "type": "string",
            },
            "value": {
                "description": _("The value to add, replace, or test."),
                # TODO: make this a union?
                "type": "any",
            },
            "from": {
                "description": _(
                    "JSON-Pointer to location within document "
                    "to move or copy the value from."
                ),
                "type": "string",
            },
        },
    },
}
