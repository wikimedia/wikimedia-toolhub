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

from .documents import ToolDocument


@doc(_("Tool search results"))
class ToolDocumentSerializer(DocumentSerializer):
    """Tool search results."""

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

    class Meta:
        """Configure serializer."""

        document = ToolDocument
        fields = ToolDocument.Django.fields.copy()
        fields.insert(fields.index("origin") + 1, "created_by")
        fields.insert(fields.index("created_date") + 1, "modified_by")


@doc(_("Tool autocomplete results"))
class AutoCompleteToolDocumentSerializer(ToolDocumentSerializer):
    """Tool autocomplete results."""

    class Meta:
        """Configure serializer."""

        document = ToolDocument
        fields = ["name", "title"]
