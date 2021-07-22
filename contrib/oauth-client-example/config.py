# This file is part of the Toolhub OAuth client demo application.
#
# Copyright (C) 2021 Bryan Davis and contributors
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging.config
import os

from envparse import env


logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(module)s %(levelname)s: %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            },
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["wsgi"],
        },
    }
)


DEBUG = env.bool("FLASK_DEBUG", default=False)
SECRET_KEY = env.str(
    "SECRET_KEY",
    default=os.urandom(128).decode("utf8", errors="ignore"),
)
SERVER_NAME = env.str("SERVER_NAME", default="localhost:8002")
TOOLHUB_CLIENT_ID = env.str("TOOLHUB_CLIENT_ID")
TOOLHUB_CLIENT_SECRET = env.str("TOOLHUB_CLIENT_SECRET")
TOOLHUB_ACCESS_TOKEN_URL = env.str(
    "TOOLHUB_ACCESS_TOKEN_URL",
    default="http://web:8000/o/token/",
)
TOOLHUB_AUTHORIZE_URL = env.str(
    "TOOLHUB_AUTHORIZE_URL",
    default="http://localhost:8000/o/authorize/",
)
TOOLHUB_API_BASE_URL = env.str(
    "TOOLHUB_API_BASE_URL",
    default="http://web:8000/api/",
)
