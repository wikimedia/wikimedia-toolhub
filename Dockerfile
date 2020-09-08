FROM python:3.7-buster

ENV PYTHONBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_ROOT="/srv/poetry" \
    POETRY_BIN_DIR="/srv/poetry/bin" \
    POETRY="/srv/poetry/bin/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0

# Install poetry in an isolated venv
RUN python3 -m venv $POETRY_ROOT \
    && $POETRY_BIN_DIR/pip3 install poetry

WORKDIR /usr/src/app
COPY pyproject.toml poetry.lock ./
RUN $POETRY export -f requirements.txt -o requirements.txt \
    && pip3 install -r requirements.txt

COPY . ./
