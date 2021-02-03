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

from drf_spectacular.plumbing import ResolvedComponent
from drf_spectacular.plumbing import build_array_type
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.plumbing import build_object_type
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.types import OpenApiTypes


def build_standard_type(obj, **kwargs):
    """Build a basic type with optional add ons."""
    schema = build_basic_type(obj)
    schema.update(kwargs)
    return schema


GENERIC_ERROR = build_object_type(
    description=_("API error"),
    properties={
        "code": build_standard_type(OpenApiTypes.NUMBER),
        "message": build_standard_type(OpenApiTypes.STR),
        "status_code": build_standard_type(OpenApiTypes.NUMBER),
        "errors": build_array_type(
            build_object_type(
                properties={
                    "code": build_standard_type(OpenApiTypes.NUMBER),
                    "field": build_standard_type(OpenApiTypes.STR),
                    "message": build_standard_type(OpenApiTypes.STR),
                },
                required=["field", "message"],
            ),
        ),
    },
    required=["code", "message", "errors"],
)


def postprocess_schema_responses(result, generator, **kwargs):  # noqa: W0613
    """Workaround to set a default response for endpoints.

    Workaround suggested at
    <https://github.com/tfranzel/drf-spectacular/issues/119#issuecomment-656970357>
    for the missing drf-spectacular feature discussed in
    <https://github.com/tfranzel/drf-spectacular/issues/101>.
    """

    def create_component(name, schema, type_=ResolvedComponent.SCHEMA):
        """Register a component and return a reference to it."""
        component = ResolvedComponent(
            name=name,
            type=type_,
            schema=schema,
            object=name,
        )
        generator.registry.register_on_missing(component)
        return component

    error = create_component("GenericError", GENERIC_ERROR)
    error_schema = {
        "content": {
            "application/json": {
                "schema": error.ref,
            },
        },
    }
    default_error = create_component("DefaultError", error_schema, "responses")

    for path in result["paths"].values():
        for method in path.values():
            method["responses"]["default"] = default_error.ref

    result["components"] = generator.registry.build(
        spectacular_settings.APPEND_COMPONENTS
    )

    return result
