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
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view

from rest_framework import permissions
from rest_framework import viewsets

from .models import LogEntry
from .serializers import LogEntrySerializer


class TargetFilter(filters.CharFilter):
    """Custom filter for auditlog targets.

    Used to remap internal type names to names matching serialization.
    """

    remap_names = {
        "user": "toolhubuser",
    }

    def filter(self, qs, value):  # noqa: A003
        """Add filter to queryset."""
        return super().filter(qs, self.remap_names.get(value, value))


class LogEntryFilter(filters.FilterSet):
    """Custom query filters for LogEntry endpoints."""

    action = filters.MultipleChoiceFilter(
        field_name="action",
        lookup_expr="exact",
        choices=LogEntry.ACTION_CHOICES,
        help_text=format_lazy(
            "{}\n{}",
            _("Only show logs for the given action types."),
            "".join(  # NOTE: this inner bit will be rendered in the en locale
                "* {} = {}\n".format(c[0], c[1])
                for c in LogEntry.ACTION_CHOICES
            ),
        ),
    )
    target_type = TargetFilter(
        field_name="content_type__model",
        lookup_expr="exact",
        help_text=_("Only show logs for the given target type."),
    )
    before = filters.IsoDateTimeFilter(
        field_name="timestamp",
        lookup_expr="lte",
        help_text=_(
            "Only show logs occurring before the given date and time."
        ),
    )
    after = filters.IsoDateTimeFilter(
        field_name="timestamp",
        lookup_expr="gte",
        help_text=_("Only show logs occurring after the given date and time."),
    )
    user = filters.CharFilter(
        field_name="user__username",
        lookup_expr="exact",
        help_text=_("Only show logs for the given user."),
    )


@extend_schema_view(
    list=extend_schema(
        description=_("""List all log entries."""),
    ),
    retrieve=extend_schema(
        description=_("""Info for a specific log entry."""),
    ),
)
class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """LogEntries."""

    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = LogEntryFilter
    ordering = ["-timestamp"]
