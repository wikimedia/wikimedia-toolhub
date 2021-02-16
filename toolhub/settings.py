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
"""
Django settings for toolhub project.

Configuration variations for different deployments (dev, test, prod) are
managed using environment variables. See FIXME for the available variables and
their expected use.
"""
import logging
import os
import sys

from django.utils.translation import gettext_lazy as _

import environ


TOOLHUB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TOOLHUB_DIR)
VUE_DIR = os.path.join(BASE_DIR, "vue")

env = environ.Env()
env.smart_cast = False

# Hack so that we can guard things that will probably fail miserably in test
# like contacting an external server
TEST_MODE = "test" in sys.argv

# == Logging & Tracing ==
logging.captureWarnings(True)
LOGGING_HANDLERS = env.list("LOGGING_HANDLERS", default=["console"])
LOGGING_LEVEL = env.str("LOGGING_LEVEL", default="WARNING")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "incremental": False,
    "filters": {
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"}
    },
    "formatters": {
        "line": {
            "format": "%(asctime)s [%(request_id)s] %(name)s %(levelname)s: "
            "%(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "line",
            "filters": ["request_id"],
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": env.str("LOGGING_FILE_FILENAME", default="/dev/null"),
            "filters": ["request_id"],
            "formatter": "line",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "django": {
            "handlers": LOGGING_HANDLERS,
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": LOGGING_HANDLERS,
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "django.security": {
            "handlers": LOGGING_HANDLERS,
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "django.utils.autoreload": {
            "handlers": LOGGING_HANDLERS,
            "level": "WARNING",
            "propagate": False,
        },
        "py.warnings": {
            "handlers": LOGGING_HANDLERS,
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
    },
    "root": {
        "handlers": LOGGING_HANDLERS,
        "level": LOGGING_LEVEL,
    },
}

LOG_REQUEST_ID_HEADER = env.str(
    "LOG_REQUEST_ID_HEADER", default="HTTP_X_REQUEST_ID"
)
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = env.str(
    "REQUEST_ID_RESPONSE_HEADER", default="X-Request-ID"
)
NO_REQUEST_ID = "none"
OUTGOING_REQUEST_ID_HEADER = env.str(
    "OUTGOING_REQUEST_ID_HEADER", default="X-Request-ID"
)

# == Django settings ==
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ==== Third-party apps ====
    "django_filters",
    "drf_spectacular",
    "oauth2_provider",
    "rest_framework",
    "reversion",
    "reversion_compare",
    "social_django",
    "webpack_loader",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
    # ==== Local apps ====
    "toolhub.apps.auditlog",
    "toolhub.apps.crawler",
    "toolhub.apps.toolinfo",
    "toolhub.apps.user",
    "vue",
]

MIDDLEWARE = [
    "log_request_id.middleware.RequestIDMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "toolhub.apps.auditlog.middleware.LogEntryUserMiddleware",
]

ROOT_URLCONF = "toolhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(TOOLHUB_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "toolhub.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env.str("DB_NAME", default=":memory:"),
        "USER": env.str("DB_USER", default=""),
        "PASSWORD": env.str("DB_PASSWORD", default=""),
        "HOST": env.str("DB_HOST", default=""),
        "PORT": env.int("DB_PORT", default=0),
    }
}
if "mysql" in DATABASES["default"]["ENGINE"]:  # pragma: no cover
    # Make Django and MySQL play nice
    # https://blog.ionelmc.ro/2014/12/28/terrible-choices-mysql/
    # NOTE: use of utf8mb4 charset assumes innodb_large_prefix on the hosting
    # MySQL server. If not enabled, you will receive errors mentioning
    # "Specified key was too long; max key length is 767 bytes" for UNIQUE
    # indices on varchar(255) fields.
    DATABASES["default"]["OPTIONS"] = {
        "sql_mode": "TRADITIONAL",
        "charset": "utf8mb4",
        "init_command": "SET character_set_connection=utf8mb4,"
        "collation_connection=utf8mb4_unicode_ci;"
        "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED",
    }

CACHES = {
    "default": {
        "BACKEND": env.str(
            "CACHE_BACKEND",
            default="django.core.cache.backends.locmem.LocMemCache",
        ),
        "LOCATION": env.str("CACHE_LOCATION", default=""),
        "KEY_PREFIX": "toolhub",
        "VERSION": 1,
    }
}

# === Search ===
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": env.str("ES_HOSTS", default="localhost:9200"),
    }
}
ELASTICSEARCH_DSL_INDEX_SETTINGS = {
    "number_of_replicas": env.int("ES_INDEX_REPLICAS", default=0),
    "number_of_shards": env.int("ES_INDEX_SHARDS", default=1),
}
ELASTICSEARCH_DSL_AUTOSYNC = env.bool("ES_DSL_AUTOSYNC", default=True)
ELASTICSEARCH_DSL_PARALLEL = env.bool("ES_DSL_PARALLEL", default=True)

# === Authentication ===
AUTH_USER_MODEL = "user.ToolhubUser"
LOGIN_URL = "/user/login/"
LOGIN_REDIRECT_URL = "vue:main"
LOGOUT_REDIRECT_URL = "vue:main"

AUTHENTICATION_BACKENDS = [
    "toolhub.oauth.WikimediaOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SOCIAL_AUTH_WIKIMEDIA_BASE_URL = env.str(
    "WIKIMEDIA_OAUTH2_URL", default="https://meta.wikimedia.org/w/rest.php"
)
SOCIAL_AUTH_WIKIMEDIA_KEY = env.str("WIKIMEDIA_OAUTH2_KEY")
SOCIAL_AUTH_WIKIMEDIA_SECRET = env.str("WIKIMEDIA_OAUTH2_SECRET")

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = False
SOCIAL_AUTH_SLUGIFY_USERNAMES = False
SOCIAL_AUTH_CLEAN_USERNAMES = False
SOCIAL_AUTH_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
SOCIAL_AUTH_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = env.str(
    "STATIC_ROOT", default=os.path.join(BASE_DIR, "staticfiles")
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    os.path.join(VUE_DIR, "dist"),
    ("jsonschema", os.path.join(BASE_DIR, "jsonschema")),
)
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_INDEX_FILE = True

LOCALE_PATHS = [
    os.path.join(TOOLHUB_DIR, "locale"),
]

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("REQUIRE_HTTPS", default=False)
SECURE_SSL_HOST = env.str("SSL_CANONICAL_HOST", "toolhub.wikimedia.org")

# === Sessions ===
# Cache session data in memcached but keep db persistance as backup
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_SECURE = env.bool("REQUIRE_HTTPS", default=False)

# === CSRF ===
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.bool("REQUIRE_HTTPS", default=False)

# === django.middleware.security.SecurityMiddleware flags ===
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# TODO: CSP
# TODO: Referrer-Policy

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(VUE_DIR, "dist/webpack-stats.json"),
    },
}

OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": _("Read scope"),
        "write": _("Write scope"),
    },
    "ERROR_RESPONSE_WITH_SCOPES": True,
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "toolhub.pagination.CustomPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "drf_spectacular.contrib.django_filters.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "EXCEPTION_HANDLER": "rest_framework_friendly_errors.handlers.friendly_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": r"/api",
    "SERVE_INCLUDE_SCHEMA": False,
    "TITLE": _("Toolhub API"),
    "LICENSE": {
        "name": "GPL-3.0-or-later",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html",
    },
    "VERSION": "0.0.1",
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
    "OAUTH2_FLOWS": ["authorizationCode"],
    "OAUTH2_AUTHORIZATION_URL": "/o/authorize/",
    "OAUTH2_TOKEN_URL": "/o/token/",
    "POSTPROCESSING_HOOKS": [
        "toolhub.openapi.postprocess_schema_responses",
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
}

FRIENDLY_ERRORS = {
    "VALIDATOR_ERRORS": {
        "JSONSchemaValidator": 3101,
    },
    "EXCEPTION_DICT": {
        "ConflictingState": 4090,
    },
}
