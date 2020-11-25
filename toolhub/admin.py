# Copyright (c) 2020 Wikimedia Foundation and contributors.
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
from django.contrib import admin


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """Read-only integration with Django's admin console."""

    # Inspired by https://stackoverflow.com/a/19884095/8171
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        """Report all fields as readonly."""
        ro = list(self.readonly_fields)
        ro.extend(field.name for field in obj._meta.fields)
        ro.extend(field.name for field in obj._meta.many_to_many)
        return ro

    def has_add_permission(self, request):
        """Disallow add."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disallow delete."""
        return False


class ReadOnlyTabularInline(admin.TabularInline):
    """Read-only integration with Django's admin console."""

    # Inspired by https://stackoverflow.com/a/19884095/8171
    extra = 0
    can_delete = False
    editable_fields = []
    readonly_fields = []
    exclude = []

    def get_readonly_fields(self, request, obj=None):
        """Report all fields as readonly."""
        ro = list(self.readonly_fields)
        ro.extend(
            field.name
            for field in self.model._meta.fields
            if field.name not in self.editable_fields
            and field.name not in self.exclude
        )
        return ro

    def has_add_permission(self, request, obj=None):
        """Disallow add."""
        return False
