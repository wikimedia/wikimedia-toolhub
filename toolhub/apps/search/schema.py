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

from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.plumbing import build_array_type
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.plumbing import build_object_type
from drf_spectacular.plumbing import build_parameter_type


USER = {
    "type": "object",
    "description": _("User information"),
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
    },
}

FACET_RESPONSE = build_object_type(
    description=_("Faceted classification"),
    additionalProperties=build_object_type(
        properties={
            "doc_count": build_basic_type(int),
        },
        additionalProperties=build_object_type(
            properties={
                "meta": build_object_type(
                    properties={
                        "param": build_basic_type(str),
                        "missing": build_basic_type(str),
                        "missing_param": build_basic_type(str),
                    }
                ),
                "doc_count_error_upper_bound": build_basic_type(int),
                "sum_other_doc_count": build_basic_type(int),
                "buckets": build_array_type(
                    build_object_type(
                        properties={
                            "key": build_basic_type(str),
                            "doc_count": build_basic_type(int),
                        },
                    ),
                ),
            },
        ),
    ),
)


class ToolhubFilterExtension(OpenApiFilterExtension):
    """Describe django_elasticsearch_dsl_drf filters."""

    target_class = "toolhub.apps.search.views.QueryStringFilterBackend"

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        """Describe query parameters."""
        return [
            build_parameter_type(
                name=self.target.search_param,
                required=False,
                location="query",
                description=_("Query string search"),
                schema={"type": "string"},
            )
        ]


class BaseSearchFilterExtension(OpenApiFilterExtension):
    """Describe django_elasticsearch_dsl_drf filters."""

    target_class = (
        "django_elasticsearch_dsl_drf.filter_backends.BaseSearchFilterBackend"
    )
    match_subclasses = True

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        """Describe query parameters."""
        search_fields = getattr(auto_schema.view, "search_fields", None)
        if not search_fields:
            return []

        return [
            build_parameter_type(
                name=self.target.search_param,
                required=False,
                location="query",
                description=_("Search in %(fields)s")
                % {
                    "fields": _(", ").join(search_fields),
                },
                schema={"type": "string"},
            )
        ]


class FilteringFilterExtension(OpenApiFilterExtension):
    """Describe django_elasticsearch_dsl_drf filters."""

    target_class = (
        "django_elasticsearch_dsl_drf.filter_backends.FilteringFilterBackend"
    )
    match_subclasses = True

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        """Describe query parameters."""
        filter_fields = getattr(auto_schema.view, "filter_fields", None)
        if not filter_fields:
            return []

        return [
            build_parameter_type(
                name="{}__{}".format(field_name, lookup),
                required=False,
                location="query",
                schema={"type": "string"},
            )
            for field_name, config in filter_fields.items()
            for lookup in config.get("lookups", [])
        ]


class NestedFilteringFilterExtension(OpenApiFilterExtension):
    """Describe django_elasticsearch_dsl_drf filters."""

    target_class = (
        "django_elasticsearch_dsl_drf.filter_backends."
        "NestedFilteringFilterBackend"
    )
    match_subclasses = True

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        """Describe query parameters."""
        filter_fields = getattr(auto_schema.view, "filter_fields", None)
        if not filter_fields:
            return []

        return [
            build_parameter_type(
                name=field_name,
                required=False,
                location="query",
                schema={"type": "string"},
            )
            for field_name in filter_fields
        ]


class PostFilterFilteringFilterExtension(NestedFilteringFilterExtension):
    """Describe django_elasticsearch_dsl_drf filters."""

    target_class = (
        "django_elasticsearch_dsl_drf.filter_backends."
        "PostFilterFilteringFilterBackend"
    )
    match_subclasses = True


class OrderingFilterExtension(OpenApiFilterExtension):
    """Describe django_elasticsearch_dsl_drf filters."""

    target_class = (
        "django_elasticsearch_dsl_drf.filter_backends.OrderingFilterBackend"
    )
    match_subclasses = True

    def get_schema_operation_parameters(self, auto_schema, *args, **kwargs):
        """Describe query parameters."""
        return [
            build_parameter_type(
                name=self.target.ordering_param,
                required=False,
                location="query",
                schema={"type": "string"},
                description=_("Field to use when ordering results."),
            )
        ]
