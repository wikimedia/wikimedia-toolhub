# Copyright (c) 2022 Wikimedia Foundation and contributors.
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
from contextlib import contextmanager

import reversion

from .models import RevisionMetadata


@contextmanager
def reversion_context(user, comment=None):
    """Custom context manager for creating new revision"""
    with reversion.create_revision():
        reversion.add_meta(RevisionMetadata)
        reversion.set_user(user)
        if comment is not None:
            reversion.set_comment(comment)
        yield
