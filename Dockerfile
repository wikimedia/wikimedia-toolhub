# Dockerfile for *local development*.
# This setup is not ideal for production deployments due to in inclusion of
# development tools.
FROM python:3.7-buster

ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install dockerize for better docker-compose integration.
ENV DOCKERIZE_VERSION=v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Install poetry
ENV POETRY_VERSION=1.0.10 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_PATH=/srv/poetry
RUN pip3 install poetry==${POETRY_VERSION}

# Switch to an unprivledged user
RUN mkdir -p $POETRY_VIRTUALENVS_PATH \
    && chown www-data:www-data $POETRY_VIRTUALENVS_PATH \
    && mkdir -p /var/www/.cache \
    && chown www-data:www-data /var/www/.cache \
    && mkdir -p /var/www/.pylint.d \
    && chown www-data:www-data /var/www/.pylint.d
USER www-data

WORKDIR /usr/src/app

# Install runtime and dev python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Import the application. When developing for Toolhub you should mount your
# local working copy over WORKDIR so that changes can be seen live inside the
# container.
COPY . ./

# Run Django's `runserver` mode
EXPOSE 8000
CMD [ \
    "poetry", "run", \
    "python3", "manage.py", "runserver", "0.0.0.0:8000" \
]
