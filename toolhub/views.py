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
import json
import logging

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


ALLOWED_PREFIXES = (
    "http://",
    "https://",
    "ws://",
    "wss://",
    "data",
    "eval",
    "inline",
)

logger = logging.getLogger(__name__)
csp_logger = logging.getLogger("csp-report")


@require_POST
@csrf_exempt
def csp_report(req):
    """Accept a Content-Security-Policy violation report from a client."""
    content_length = req.META.get("CONTENT_LENGTH", None)
    if content_length is not None and int(content_length) > 8192:
        # limit abuse by limiting POST size to 8k
        return HttpResponse("", status=413)

    raw_report = req.body
    if isinstance(raw_report, bytes):
        raw_report = raw_report.decode("utf-8")

    try:
        payload = json.loads(raw_report)
    except ValueError:
        # Ignore malformed reports
        return HttpResponse("", status=400)

    if "csp-report" not in payload:
        return HttpResponse("", status=400)

    report = payload["csp-report"]
    resp = HttpResponse("", status=204)

    uri = report["blocked-uri"]
    if not any(uri.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        # Ignore reports for things like safari-extension://...
        logger.debug("Ignoring disallowed blocked-uri prefix: %s", uri)
        return resp

    src_file = report.get("source-file", None)
    if src_file is None:
        # Ignore reports with no source-file supplied. This is a common
        # signature for errors from client controlled code like browser
        # plugins that inject content into all pages.
        logger.debug("Ignoring report without a source-file attribute.")
        return resp
    elif not any(src_file.startswith(p) for p in ALLOWED_PREFIXES):
        # Ignore reports from files like moz-extension://...
        logger.debug("Ignoring disallowed source-file prefix: %s", src_file)
        return resp

    if "line-number" not in report or int(report["line-number"]) <= 1:
        # Ignore reports of errors on line 0 & 1. This is a common signature
        # for CSP errors triggered by client controlled code (such as browser
        # plugins which inject CSS/JS into all pages).
        return resp

    csp_logger.warning(raw_report)
    return resp


def healthz(req):  # noqa: W0613
    """Trivial 'is this process alive' check."""
    return JsonResponse({"status": "OK"})
