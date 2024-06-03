#!/bin/bash
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

set -Eeuo pipefail

# Send shutdown signal to envoy process running at 127.0.0.1:1666
# https://envoyproxy.io/docs/envoy/latest/operations/admin#post--quitquitquit
# Bug: T292861
kill_envoy() {
    printf "POST /quitquitquit HTTP/1.0\r\n\r\n" >/dev/tcp/127.0.0.1/1666
}
trap 'kill_envoy' EXIT

poetry run python3 /srv/app/manage.py crawl --quiet
