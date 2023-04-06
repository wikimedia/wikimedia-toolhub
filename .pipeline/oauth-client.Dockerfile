# Dockerfile for *local development*.
# Generated by Blubber from .pipeline/blubber.yaml
FROM docker-registry.wikimedia.org/python3-bullseye:latest AS oauth-client
USER 0
ENV HOME="/root"
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install -y "build-essential" "default-libmysqlclient-dev" "gettext" "git" "python3-dev" "python3-venv" && rm -rf /var/lib/apt/lists/*
RUN python3 "-m" "pip" "install" "-U" "setuptools!=60.9.0" && python3 "-m" "pip" "install" "-U" "wheel" "tox" "pip"
ENV POETRY_VIRTUALENVS_PATH="/opt/lib/poetry"
RUN python3 "-m" "pip" "install" "-U" "poetry==1.3.1"
ARG LIVES_AS="somebody"
ARG LIVES_UID=65533
ARG LIVES_GID=65533
RUN (getent group "$LIVES_GID" || groupadd -o -g "$LIVES_GID" -r "$LIVES_AS") && (getent passwd "$LIVES_UID" || useradd -l -o -m -d "/home/$LIVES_AS" -r -g "$LIVES_GID" -u "$LIVES_UID" "$LIVES_AS") && mkdir -p "/srv/app" && chown "$LIVES_UID":"$LIVES_GID" "/srv/app" && mkdir -p "/opt/lib" && chown "$LIVES_UID":"$LIVES_GID" "/opt/lib"
ARG RUNS_AS="runuser"
ARG RUNS_UID=900
ARG RUNS_GID=900
RUN (getent group "$RUNS_GID" || groupadd -o -g "$RUNS_GID" -r "$RUNS_AS") && (getent passwd "$RUNS_UID" || useradd -l -o -m -d "/home/$RUNS_AS" -r -g "$RUNS_GID" -u "$RUNS_UID" "$RUNS_AS")
USER $LIVES_UID
ENV HOME="/home/somebody"
WORKDIR "/srv/app"
ENV DJANGO_SETTINGS_MODULE="toolhub.settings" PIP_DISABLE_PIP_VERSION_CHECK="on" PIP_NO_CACHE_DIR="off" PYTHONDONTWRITEBYTECODE="1" PYTHONUNBUFFERED="1"
COPY --chown=$LIVES_UID:$LIVES_GID ["contrib/oauth-client-example/pyproject.toml", "contrib/oauth-client-example/poetry.lock", "./"]
RUN mkdir -p "/opt/lib/poetry"
RUN poetry "install" "--no-root" "--no-dev"
COPY --chown=$LIVES_UID:$LIVES_GID ["contrib/oauth-client-example", "./"]
USER $RUNS_UID
ENV HOME="/home/$RUNS_AS"
ENTRYPOINT ["/bin/bash", "-c", "poetry run python3 -m flask run --host 0.0.0.0 --port 8000"]

LABEL blubber.variant="oauth-client" blubber.version="0.9.0+2638669"
