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
from django.core.management.base import BaseCommand

from toolhub.apps.crawler.tasks import Crawler


class Command(BaseCommand):
    """Run the crawler."""

    help = "Run the crawler"  # noqa: A003

    def handle(self, *args, **options):
        """Execute the command."""
        spider = Crawler()
        run = spider.crawl()
        self.stdout.write(repr(run))
        for url in run.crawlerrunurl_set.all():
            self.stdout.write(repr(url))
