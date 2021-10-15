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
import socket

import ecs_logging


class ECSFormatter(ecs_logging.StdlibFormatter):
    """Logging formattter conforming to the ECS standard."""

    _REMAPPED_FIELDS = {
        # This should end up in "trace.id", but we need to set it as
        # "elasticapm_trace_id" because the parent class blindly
        # overwrites "trace.id" with `pop("elasticapm_trace_id", None)`.
        "request_id": "elasticapm_trace_id",
        "status_code": "http.response.status_code",
    }

    def __init__(self, **kwargs):
        """Initialize object."""
        kwargs["exclude_fields"] = [
            "log.original",  # duplicate of "message"
            "server_time",
        ]
        super().__init__(**kwargs)

    def format_to_ecs(self, record):
        """Convert a LogRecord to an ECS record."""
        ecs = super().format_to_ecs(self._preprocess_record(record))

        # T292574: Report record as ECS v1.7.0
        ecs["ecs"]["version"] = "1.7.0"

        # T293541: Add service.type to ECS log events
        if "service" not in ecs:
            ecs["service"] = {}
        ecs["service"]["type"] = "toolhub"

        return ecs

    def _preprocess_record(self, record):
        """Pre-process LogRecord."""

        def _pop(key, default=None):
            """Pop an attribute from our record."""
            value = default
            if hasattr(record, key):
                value = getattr(record, key)
                del record.__dict__[key]
            return value

        def _push(key, value):
            """Push an attribute into our record."""
            record.__dict__[key] = value

        for orig, remap in self._REMAPPED_FIELDS.items():
            value = _pop(orig)
            if value is not None:
                _push(remap, value)

        request = _pop("request")
        if request is not None and isinstance(request, socket.socket):
            client = request.getpeername()
            _push("client.address", client[0])
            _push("client.port", client[1])
            server = request.getsockname()
            _push("server.address", server[0])
            _push("server.port", server[1])

        return record
