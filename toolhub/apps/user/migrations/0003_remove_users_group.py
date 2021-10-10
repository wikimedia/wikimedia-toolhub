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
from django.conf import settings
from django.db import migrations
from django.db import models


def apply_migration(apps, schema_editor):
    """Create default user groups."""
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Users").delete()


def revert_migration(apps, schema_editor):
    """Remove default user groups."""
    Group = apps.get_model("auth", "Group")
    Group.objects.bulk_create(Group(name="Users"))


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0002_setup_groups'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
