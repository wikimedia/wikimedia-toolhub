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
import io
import logging
import threading


DEFAULT_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s"
COMPACT_FORMAT = "%(levelname)s: %(message)s"


class LogCaptureContext:
    """Collect log events in a buffer."""

    def __init__(
        self,
        logger=None,
        level=logging.DEBUG,
        fmt=DEFAULT_FORMAT,
        filters=None,
    ):
        """Setup context."""
        self.logger = logger
        if logger is None:
            self.logger = logging.getLogger()
        self.level = level
        self.format = fmt
        self.stream = io.StringIO()
        self.filters = filters or []
        self.handler = None

    def __enter__(self):
        """Enter context."""
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setLevel(self.level)
        self.handler.setFormatter(logging.Formatter(self.format))
        for filter_ in self.filters:
            self.handler.addFilter(filter_)
        self.logger.addHandler(self.handler)
        return self.stream

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context."""
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
            self.handler.close()
        if not self.stream.closed:
            self.stream.close()


class CaptureCrawlLogs(LogCaptureContext):
    """Collect logs and store in the given model."""

    def __init__(self, model, field="logs"):
        """Setup context."""
        self.model = model
        self.field = field
        thread_id = threading.get_ident()
        filters = [
            # Only collect records for toolhub classes
            logging.Filter(name="toolhub"),
            # Only collect records emitted by the same thread that called us
            lambda r: r.thread == thread_id,
        ]
        super().__init__(
            level=logging.INFO,
            fmt=COMPACT_FORMAT,
            filters=filters,
        )

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context."""
        setattr(self.model, self.field, self.stream.getvalue())
        self.model.save()
        super().__exit__(exc_type, exc_value, traceback)
