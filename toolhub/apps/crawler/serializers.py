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
from toolhub.apps.user.serializers import UserSerializer
from toolhub.serializers import ModelSerializer

from .models import CrawledUrl
from .models import CrawlerRun
from .models import CrawlerRunUrl


class CrawledUrlSerializer(ModelSerializer):
    """Details of an URL that has been registered for crawling."""

    created_by = UserSerializer(many=False, read_only=True)
    modified_by = UserSerializer(many=False, read_only=True)

    class Meta:
        """Configure serializer."""

        model = CrawledUrl
        fields = "__all__"


class EditCrawledUrlSerializer(ModelSerializer):
    """An URL that will be crawled."""

    class Meta:
        """Configure serializer."""

        model = CrawledUrl
        fields = ["url"]


class SummaryCrawledUrlSerializer(ModelSerializer):
    """An URL that will be crawled."""

    class Meta:
        """Configure serializer."""

        model = CrawledUrl
        fields = ["id", "url"]


class CrawlerRunUrlSerializer(ModelSerializer):
    """Information about a single URL processed during a crawler run."""

    # url = SummaryCrawledUrlSerializer(read_only=True)

    class Meta:
        """Configure serializer."""

        model = CrawlerRunUrl
        fields = [
            "id",
            "run_id",
            "url_id",
            "status_code",
            "redirected",
            "elapsed_ms",
            "schema",
            "valid",
        ]


class CrawlerRunSerializer(ModelSerializer):
    """Summary of a single run of the crawler."""

    class Meta:
        """Configure serializer."""

        model = CrawlerRun
        fields = ["id", "start_date", "end_date", "new_tools"]
