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
from django.conf import settings
from django.db import models

from django_prometheus.models import ExportModelOperationsMixin

from toolhub.apps.auditlog.signals import registry
from toolhub.apps.toolinfo.models import Tool


@registry.register()
class Url(ExportModelOperationsMixin("url"), models.Model):
    """A URL that the crawler should fetch."""

    url = models.URLField(max_length=255, unique=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        db_index=True,
        on_delete=models.CASCADE,
    )
    created_date = models.DateTimeField(
        auto_now_add=True, blank=True, editable=False, db_index=True
    )

    def __str__(self):
        return self.url

    def delete(self, *args, **kwargs):
        """Overide model delete method to also delete related tools"""
        self.delete_related_tools()
        super().delete(*args, **kwargs)

    def delete_related_tools(self):
        """Delete tools related to the URL about to be deleted"""
        last_run = self.crawler_runs.order_by("-id").first()
        if last_run:
            last_run.tools.filter(deleted__isnull=True).distinct().delete()

    @property
    def auditlog_label(self):
        """Get label for use in auditlog output."""
        return self.url


class Run(ExportModelOperationsMixin("run"), models.Model):
    """A run of the crawler."""

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    new_tools = models.PositiveIntegerField(blank=True, default=0)
    updated_tools = models.PositiveIntegerField(blank=True, default=0)
    total_tools = models.PositiveIntegerField(blank=True, default=0)

    def __str__(self):
        return "id={}; start={:%Y-%m-%d %H:%M}".format(
            self.id,
            self.start_date,
        )


class RunUrl(ExportModelOperationsMixin("runurl"), models.Model):
    """Information about a URL crawled during a Run."""

    run = models.ForeignKey(
        Run,
        related_name="urls",
        on_delete=models.CASCADE,
    )
    url = models.ForeignKey(
        Url,
        related_name="crawler_runs",
        on_delete=models.CASCADE,
    )
    status_code = models.PositiveSmallIntegerField()
    redirected = models.BooleanField(default=False)
    elapsed_ms = models.PositiveIntegerField(default=0)
    schema = models.CharField(blank=True, max_length=32, null=True)
    valid = models.BooleanField(default=False)
    tools = models.ManyToManyField(
        Tool,
        related_name="crawler_runs",
    )
    logs = models.TextField(blank=True)

    def __str__(self):
        return "id={}; run: {}; url: {}; status_code: {}; valid: {}".format(
            self.id,
            self.run.id,
            self.url.id,
            self.status_code,
            self.valid,
        )
