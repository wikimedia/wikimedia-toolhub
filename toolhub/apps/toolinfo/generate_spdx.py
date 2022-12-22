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
import datetime
import pkg_resources
import pprint
import sys

import requests


TEMPLATE = """\
# Copyright (c) {year} Wikimedia Foundation and contributors.
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

SPDX_GIT_TAG = "{git_tag}"

SPDX_LICENSES = {licenses}
"""


def get_latest_release_tag():
    """Get the latest release tag for spdx/license-list-data."""
    url = "https://api.github.com/repos/spdx/license-list-data/tags"
    r = requests.get(url)
    tags = r.json()
    latest = "0"
    for tag in tags:
        if pkg_resources.parse_version(
            tag["name"]
        ) > pkg_resources.parse_version(latest):
            latest = tag["name"]
    return latest


def main():
    """Generate a module containing a dict of SPDX license data.

    Borrows heavily from Michael Pöhn's defunct spdx-license-list package
    found at <https://gitlab.com/uniqx/spdx-license-list>.
    """
    git_tag = get_latest_release_tag()
    url = "https://github.com/{project}/raw/{tag}/json/licenses.json".format(
        project="spdx/license-list-data", tag=git_tag
    )
    r = requests.get(url)

    licenses = {}
    for entry in r.json()["licenses"]:
        del entry["detailsUrl"]
        del entry["reference"]
        del entry["seeAlso"]
        if "isOsiApproved" not in entry:
            entry["isOsiApproved"] = False
        if "isFsfLibre" not in entry:
            entry["isFsfLibre"] = False
        entry["referenceNumber"] = int(entry["referenceNumber"])
        licenses[entry["licenseId"]] = entry

    raw = TEMPLATE.format(
        year=datetime.datetime.now().year,
        git_tag=git_tag,
        licenses=pprint.pformat(licenses),
    )
    print(raw)


if __name__ == "__main__":
    sys.exit(main())
