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
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils import language_data
from .spdx import SPDX_LICENSES


url_validator = validators.URLValidator(schemes=["http", "https"])


def validate_language_code(value):
    """Raise ValidationError if value is not a recognized language code."""
    if not language_data.is_known(value):
        raise ValidationError(
            _("%(value)s is not a recognized language code."),
            code="invalid_language",
            params={"value": value},
        )


def validate_language_code_list(value):
    """Raise ValidationError if value is not a list of language codes."""
    if not isinstance(value, list):
        raise ValidationError(
            _("Expected a list of language codes but found %(type)s"),
            code="invalid_list",
            params={"type": type(value)},
        )
    for code in value:
        validate_language_code(code)


def validate_spdx(value):
    """Raise ValidationError if value is not an SPDX license identifier."""
    if value not in SPDX_LICENSES:
        raise ValidationError(
            _("%(value)s is not a known SPDX license identifier."),
            code="invalid_spdx",
            params={"value": value},
        )


def validate_url_mutilingual(value):
    """Raise ValidationError if value is not a well formed url_multilingual."""
    if not isinstance(value, dict):
        raise ValidationError(
            _("Expected a url_multilingual dict but found %(type)s"),
            code="invalid_list",
            params={"type": type(value)},
        )
    if "language" not in value:
        raise ValidationError(
            _("Url_multilingual missing 'language' property."),
            code="missing_language",
        )
    validate_language_code(value["language"])

    if "url" not in value:
        raise ValidationError(
            _("Url_multilingual missing 'url' property."),
            code="missing_url",
        )
    url_validator(value["url"])


def validate_url_mutilingual_list(value):
    """Raise ValidationError if value is not a list of well formed values."""
    if not isinstance(value, list):
        raise ValidationError(
            _("Expected a list of language codes but found %(type)s"),
            code="invalid_list",
            params={"type": type(value)},
        )
    for url in value:
        validate_url_mutilingual(url)
