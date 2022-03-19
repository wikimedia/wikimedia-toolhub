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

from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from reversion.models import Version

from .serializers import RevisionSerializer


class RecentChangesFilter(filters.FilterSet):
    """Custom query filters for RecentChanges endpoints."""

    user = filters.CharFilter(
        field_name="revision__user__username",
        lookup_expr="exact",
        help_text=_("Only show recent changes by the given user."),
    )
    target_type = filters.CharFilter(
        field_name="content_type__model",
        lookup_expr="exact",
        help_text=_("Only show recent changes for the given target type."),
    )
    suppressed = filters.BooleanFilter(
        field_name="revision__meta__suppressed",
        help_text=_(
            "Only show recent changes where suppressed field is either "
            "true or false",
        ),
    )
    patrolled = filters.BooleanFilter(
        field_name="revision__meta__patrolled",
        help_text=_(
            "Only show recent changes where patrolled field is either "
            "true or false",
        ),
    )
    date_created = filters.IsoDateTimeFromToRangeFilter(
        field_name="revision__date_created",
        help_text=_("Only show recent changes within this time range"),
    )


@extend_schema_view(
    list=extend_schema(description=_("Get a paginated list of all revisions."))
)
class RecentChangesViewSet(viewsets.ReadOnlyModelViewSet):
    """Historical revisions of a tool list."""

    serializer_class = RevisionSerializer
    permission_classes = [AllowAny]
    filterset_class = RecentChangesFilter

    def get_queryset(self):
        """Sort Version queryset by revision__date_created"""
        qs = Version.objects.select_related(
            "revision",
            "revision__meta",
            "content_type",
        )
        qs = qs.filter(content_type__model__in=["tool", "toollist"])
        # Exclude is used as a hack-around to remove Initial Revisions since
        # those do not have .meta property and will break the code.
        qs = qs.exclude(revision__meta__revision_id__isnull=True)

        return qs.order_by("-revision__date_created")
