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
import contextlib
import threading
import time
from functools import partial

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save

from .models import LogEntry


threadlocal = threading.local()


@contextlib.contextmanager
def auditlog_user(user):
    """Context manager for setting user for LogEntry creation."""
    threadlocal.auditlog = {
        "dispatch_uid": ("auditlog_user", time.time()),
    }
    pre_save_callback = partial(
        _on_log_entry_save,
        user=user,
        duid=threadlocal.auditlog["dispatch_uid"],
    )
    pre_save.connect(
        pre_save_callback,
        sender=LogEntry,
        dispatch_uid=threadlocal.auditlog["dispatch_uid"],
        weak=False,
    )

    try:
        yield
    finally:
        try:
            auditlog = threadlocal.auditlog
        except AttributeError:
            # Already disconnected
            pass
        else:
            pre_save.disconnect(
                sender=LogEntry,
                dispatch_uid=auditlog["dispatch_uid"],
            )
            del threadlocal.auditlog


def _on_log_entry_save(user, duid, sender, instance, **kwargs):  # noqa: W0613
    """Set user on LogEntry before saving."""
    try:
        auditlog = threadlocal.auditlog
    except AttributeError:
        # Already disconnected
        pass
    else:
        if duid != auditlog["dispatch_uid"]:
            # Mismatch of caller args and thread state
            return
        user_model = get_user_model()
        if (
            sender == LogEntry
            and isinstance(user, user_model)
            and instance.user is None
        ):
            instance.user = user
