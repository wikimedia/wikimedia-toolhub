# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free oftware: you can redistribute it and/or modify
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


def doc(docstring):
    """Add a translatable docstring to the decorated class or function.

    Because of the way that Django's `makemessages` finds translatable
    strings, the docstring used in the call should be wrapped in `_()`.

    .. code-block:: python

        from django.utils.translation import gettext_lazy as _
        from toolhub.decorators import doc

        @doc(_("This is the docstring that will be translatable."))
        def foo():
            pass
    """

    def decorator(func):
        func.__doc__ = docstring
        return func

    return decorator
