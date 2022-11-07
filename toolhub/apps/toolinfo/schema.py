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
import functools
import json
import urllib.parse

from django.contrib.staticfiles import finders

from drf_spectacular.extensions import OpenApiSerializerFieldExtension


SCHEMA_FILE_PATTERN = "jsonschema/toolinfo/{}.json"
CURRENT_SCHEMA = "1.2.2"


KEYWORDS = {
    "type": "array",
    "items": {
        "type": "string",
    },
    "deprecated": True,
}


@functools.lru_cache(maxsize=10)
def load_schema(version):
    """Load the given schema."""
    with open(finders.find(SCHEMA_FILE_PATTERN.format(version))) as schema:
        return json.load(schema)


def resolve_ref(document, ref):
    """Resolve a reference within the given document."""
    _, fragment = urllib.parse.urldefrag(ref)
    parts = urllib.parse.unquote(fragment.lstrip("/")).split("/")
    for part in parts:
        if isinstance(document, collections.Sequence):
            try:
                part = int(part)
            except ValueError:  # pragma: no cover
                pass
        document = document[part]
    return document


def expand_refs(obj, source):
    """Expand $ref pointers in the given sub-schema."""
    if isinstance(obj, collections.Mapping) and "$ref" in obj:
        ref = resolve_ref(source, obj["$ref"])
        del obj["$ref"]
        obj.update(ref)

    if isinstance(obj, collections.Mapping):
        obj = type(obj)((k, expand_refs(v, source)) for k, v in obj.items())
    elif isinstance(obj, collections.Sequence) and not isinstance(obj, str):
        obj = type(obj)(expand_refs(v, source) for i, v in enumerate(obj))
    return obj


def schema_for(field, oneof=None):
    """Get a jsonschema description for a given field."""
    source = load_schema(CURRENT_SCHEMA)
    raw = source["definitions"]["tool"]["properties"][field]
    expanded = expand_refs(raw, source)

    if oneof is not None:
        keep = expanded["oneOf"][oneof]
        del expanded["oneOf"]
        expanded.update(keep)
    return expanded


def _flatten_choices(choices):
    """Flatten a choices list."""
    flat = []
    for choice, value in choices:
        if isinstance(value, (list, tuple)):
            flat.extend(value)
        else:
            flat.append((choice, value))
    return flat


def choices2array(choices, item_type="string"):
    """Generate a schema based on a sequence of choices."""
    return {
        "type": "array",
        "items": {
            "type": item_type,
            "enum": [choice[0] for choice in _flatten_choices(choices)],
        },
    }


class Fix1(OpenApiSerializerFieldExtension):
    """Generate custom documentation for ForWikiField."""

    target_class = "toolhub.apps.toolinfo.serializers.ForWikiField"

    def map_serializer_field(self, auto_schema, direction):
        """Describe as an array of strings."""
        return schema_for("for_wikis", oneof=0)
