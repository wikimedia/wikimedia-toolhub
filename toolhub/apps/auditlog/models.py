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
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class LogEntryManager(models.Manager):
    """Custom manager for LogEntry models."""

    use_in_migrations = True

    def log_action(self, user, target, action, msg=None):
        """Log an action."""
        kwargs = {
            "user": user,
            "content_type": LogEntryManager._get_content_type(target),
            "action": action,
            "change_message": msg,
        }
        pk = LogEntryManager._get_pk_value(target)
        if isinstance(pk, int):
            kwargs["object_id"] = pk
        else:
            kwargs["object_pk"] = pk

        return self.model.objects.create(**kwargs)

    def get_for_object(self, instance):
        """Get log entries for a model instance."""
        if not isinstance(instance, models.Model):
            return self.none()

        ct = LogEntryManager._get_content_type(instance)
        pk = LogEntryManager._get_pk_value(instance)

        if isinstance(pk, int):
            return self.filter(content_type=ct, object_id=pk)
        return self.filter(content_type=ct, object_pk=pk)

    @staticmethod
    def _get_content_type(instance):
        """Get the ContentType for a model instance."""
        return ContentType.objects.get_for_model(instance.__class__)

    @staticmethod
    def _get_pk_value(instance):
        """Get the primary key value for a model instance."""
        pk = getattr(instance, instance._meta.pk.name, None)
        if isinstance(pk, models.Model):
            pk = LogEntryManager._get_pk_value(pk)
        return pk


class LogEntry(models.Model):
    """An audit log entry."""

    CREATE = 0
    UPDATE = 1
    DELETE = 2

    ACTION_CHOICES = (
        (CREATE, _("create")),
        (UPDATE, _("update")),
        (DELETE, _("delete")),
    )

    action_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("action time"),
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("user"),
    )
    content_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.SET_NULL,
        related_name="+",
        blank=True,
        null=True,
        verbose_name=_("content type"),
    )
    object_id = models.BigIntegerField(
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_("object id"),
    )
    object_pk = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_("object pk"),
    )
    action = models.PositiveSmallIntegerField(
        choices=ACTION_CHOICES,
        db_index=True,
        verbose_name=_("action"),
    )
    change_message = models.TextField(blank=True, null=True)

    objects = LogEntryManager()

    class Meta:
        """Metadata for model."""

        verbose_name = _("auditlog entry")
        verbose_name_plural = _("auditlog entries")

    def get_target(self):
        """Return the target object represented by this log entry."""
        if self.object_id is not None:
            return self.content_type.get_object_for_this_type(
                id=self.object_id
            )
        return self.content_type.get_object_for_this_type(pk=self.object_pk)
