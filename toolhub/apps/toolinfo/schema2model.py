# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free oftware: you can redistribute it and/or modify
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
"""Generate Django Models from a JSON Schema specification."""
# Inspired by https://gist.github.com/radzhome/d3b1586b8009ff8e1758cba6a3d92acf
import argparse
import functools
import json
import re
import sys

warn = functools.partial(print, file=sys.stderr)


def to_camel_case(snake_str):
    """Convert a snake_case label to a CamelCase label."""
    parts = snake_str.split("_")
    return parts[0].title() + "".join(p.title() for p in parts[1:])


def to_python_var(s):
    """Make a string safe for use as a Python variable name."""
    return re.sub(r"\W+|^(?=\d)", "_", s)


def required_args(key, required_fields):
    """Get the required portion of model field.

    :param key:
    :param required_fields:
    :return: str, required model string
    """
    kwargs = {}
    if key in ["id", "_id"]:
        kwargs["primary_key"] = "True"

    elif key not in required_fields:
        kwargs["null"] = "True"
        kwargs["blank"] = "True"

    return kwargs


def parse_model(  # noqa: R0912, R0914, R0915
    name, definition, schema, did_imports
):
    """Generate a Model definition for a given schema component."""
    # Make sure not list, but object
    otype = definition.get("type", "unknown")
    if otype != "object":
        warn("{}: type has to be object, got {}".format(name, otype))
        warn(definition)
        return did_imports

    model_name = to_camel_case(name)

    model_str = (
        "\n\n"
        "class {}(models.Model):\n"
        '    """Generated from json schema."""'
        "\n\n"
    ).format(model_name)

    required_fields = []
    if "required" in definition:
        required_fields = definition["required"]

    for key, props in definition["properties"].items():
        while "$ref" in props:
            # HACK! Lookup the reference and merge here if we can
            local_ref = props["$ref"].split("/")[-1]
            if local_ref in schema["definitions"]:
                props.update(schema["definitions"][local_ref])
                del props["$ref"]
            else:
                warn("{}: Unsupported ref to {}".format(key, props["$ref"]))
                break

        if "oneOf" in props:
            # Variant field, likely a one-to-many relationship
            for variant in props["oneOf"]:
                if variant["type"] == "array":
                    props = variant
                    break

        if "type" not in props:
            warn("No type found for {}".format(key))
            continue

        if props["type"] == "null":
            warn(
                "ERROR: Unsupported type null, skipping for field {}".format(
                    key
                )
            )

        kwargs = required_args(key, required_fields)
        cls = "UNKNOWN"

        # String choice field, enum
        if props["type"] == "string" and "enum" in props:
            if not props["enum"]:
                warn(
                    "ERROR: Missing enum for enum choice field {}, skipping..".format(
                        key
                    )
                )
                continue

            if len(props["enum"]) == 1:
                warn(
                    "WARNING: enum value with single choice for field {}, choice {}."
                    "".format(key, props["enum"])
                )

            cls = "models.CharField"
            kwargs["max_length"] = 255
            for choice in props["enum"]:
                if len(choice) > 255:
                    kwargs["max_length"] = len(choice)

            kwargs["choices"] = tuple(set(zip(props["enum"], props["enum"])))
            kwargs["default"] = '"{}"'.format(props["enum"][0])

        # Date time field
        elif props["type"] == "string" and props.get("format") == "date-time":
            cls = "models.DateTimeField"
            kwargs["auto_now_add"] = "False"
            kwargs["editable"] = "True"
            if key in ["created_on", "modified_on"]:
                kwargs["auto_now_add"] = "True"
                kwargs["editable"] = "False"

        elif props["type"] == "string":
            cls = "models.TextField"
            if "maxLength" in props:
                kwargs["max_length"] = props["maxLength"]
                if int(kwargs["max_length"]) <= 16384:
                    cls = "models.CharField"
            if "pattern" in props:
                kwargs["validators"] = '[{}(regex=r"{}")]'.format(
                    "validators.RegexValidator", props["pattern"]
                )

        elif props["type"] == "number" or props["type"] == "integer":
            cls = "models.IntegerField"

        elif props["type"] == "array":
            cls = "JSONField"
            kwargs["default"] = "list"

        elif props["type"] == "object":
            cls = "JSONField"
            kwargs["default"] = "dict"

        elif props["type"] == "boolean":
            cls = "models.BooleanField"
            kwargs["default"] = "False"

        model_str += "    {} = {}({})\n".format(
            to_python_var(key),
            cls,
            ", ".join("{}={}".format(k, v) for k, v in sorted(kwargs.items())),
        )

    if not did_imports:
        imports = (
            "from django.core import validators\n"
            "from django.db import models\n"
            "\n"
            "from jsonfield import JSONField\n"
        )
        model_str = imports + model_str
        did_imports = True

    print(model_str, end="")
    return did_imports


def parse_models():
    """Walk a given schema and emit models."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    filename = args.filename

    with open(filename) as f:
        schema = json.load(f)

    did_imports = False
    for name in schema["definitions"]:
        did_imports = parse_model(
            name, schema["definitions"][name], schema, did_imports
        )


if __name__ == "__main__":
    parse_models()
