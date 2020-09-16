#!/usr/bin/env bash
# Generate a .env file for local development
mkpass() {
    head /dev/urandom | LC_ALL=C tr -dc A-Za-z0-9 | head -c ${1:-20}
}
cat > ${1:?Missing target file} << _EOF
DJANGO_SECRET_KEY=$(mkpass 48)
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*
LOGGING_HANDLERS=console
LOGGING_LEVEL=INFO
DB_ENGINE=django.db.backends.mysql
DB_NAME=toolhub
DB_USER=toolhub
DB_PASSWORD=$(mkpass)
DB_HOST=db
DB_PORT=3306
DOCKER_DB_MYSQL_ROOT_PASSWORD=$(mkpass)
_EOF
