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
from django.contrib.auth import get_user_model
from django.db.models import Model
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

from .models import LogEntry


def log_create_callback(sender, instance, created, **kwargs):  # noqa: W0613
    """Handle an instance creation signal."""
    if created:
        LogEntry.objects.log_action(
            user=None,
            target=instance,
            action=LogEntry.CREATE,
        )


def log_update_callback(sender, instance, **kwargs):  # noqa: W0613
    """Handle an instance update signal."""
    if instance.pk is not None:
        user_model = get_user_model()
        # Ignore updates to user models.
        if not isinstance(instance, user_model):
            LogEntry.objects.log_action(
                user=None,
                target=instance,
                action=LogEntry.UPDATE,
            )


def log_delete_callback(sender, instance, **kwargs):  # noqa: W0613
    """Handle an instance deletion signal."""
    if instance.pk is not None:
        LogEntry.objects.log_action(
            user=None,
            target=instance,
            action=LogEntry.DELETE,
        )


class ModelRegistry:
    """A registry that tracks models to emit AuditLog instances for."""

    def __init__(self):
        """Initialize registry."""
        self._registry = {}
        self._signals = {
            post_save: log_create_callback,
            pre_save: log_update_callback,
            post_delete: log_delete_callback,
        }

    def register(self, model=None):
        """Register a model."""

        def _do_registration(cls):
            """Register a given class."""
            if not issubclass(cls, Model):
                raise TypeError("Supplied object is not a Model.")
            self._registry[cls] = True
            self._connect_signals(cls)
            return cls

        if model is None:
            # We are being called as a decorator.
            return lambda cls: _do_registration(cls)  # noqa: W0108
        _do_registration(model)

    def contains(self, model):
        """Is this model registered?"""
        return model in self._registry

    def _connect_signals(self, model):
        """Connect signals for a model."""
        for signal, reciever in self._signals.items():
            signal.connect(
                reciever,
                sender=model,
                dispatch_uid=self._dispatch_uid(signal, model),
            )

    def _dispatch_uid(self, signal, model):
        """Generate a dispatch_uid."""
        return self.__hash__(), model.__qualname__, signal.__hash__()


registry = ModelRegistry()
