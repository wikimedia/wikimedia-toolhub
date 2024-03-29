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

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from toolhub.decorators import doc

from .documents import ListDocument
from .documents import ToolDocument


class AnnotatedDocumentSerializer(DocumentSerializer):
    """Document serializer with drf_spectacular annotations."""

    _abstract = True

    def get_fields(self):
        """Decorate fields with drf_spectacular annotations."""
        field_mapping = super().get_fields()
        for name, field in self.Meta.document._fields.items():
            if name in field_mapping and hasattr(
                field, "_spectacular_annotation"
            ):
                annotations = field._spectacular_annotation  # noqa: W0212
                field_mapping[  # noqa: W0212
                    name
                ]._spectacular_annotation = annotations
        return field_mapping


@doc(_("Tool search results"))
class ToolDocumentSerializer(AnnotatedDocumentSerializer):
    """Tool search results."""

    class Meta:
        """Configure serializer."""

        document = ToolDocument
        fields = ToolDocument.Django.fields.copy()
        fields.insert(fields.index("bugtracker_url") + 1, "annotations")
        fields.insert(fields.index("origin") + 1, "created_by")
        fields.insert(fields.index("created_date") + 1, "modified_by")


@doc(_("Tool autocomplete results"))
class AutoCompleteToolDocumentSerializer(AnnotatedDocumentSerializer):
    """Tool autocomplete results."""

    class Meta:
        """Configure serializer."""

        document = ToolDocument
        fields = ["name", "title", "description"]


@doc(_("Tool search results"))
class ListDocumentSerializer(AnnotatedDocumentSerializer):
    """ToolList search results."""

    class Meta:
        """Configure serializer."""

        document = ListDocument
        fields = ListDocument.Django.fields.copy()
        fields.insert(fields.index("featured") + 1, "tools")
        fields.insert(fields.index("tools") + 1, "created_by")
        fields.insert(fields.index("created_date") + 1, "modified_by")


@doc(_("ToolList autocomplete results"))
class AutoCompleteListDocumentSerializer(AnnotatedDocumentSerializer):
    """ToolList autocomplete results."""

    class Meta:
        """Configure serializer."""

        document = ListDocument
        fields = [
            "id",
            "title",
            "description",
        ]
