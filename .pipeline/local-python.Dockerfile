# Dockerfile for *local development*.
# Generated by Blubber from .pipeline/blubber.yaml
FROM docker-registry.wikimedia.org/python3-buster:latest AS dockerize
USER 0
ENV HOME="/root"
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install -y "ca-certificates" "wget" && rm -rf /var/lib/apt/lists/*
RUN (getent group "65533" || groupadd -o -g "65533" -r "somebody") && (getent passwd "65533" || useradd -l -o -m -d "/home/somebody" -r -g "somebody" -u "65533" "somebody") && mkdir -p "/srv/dockerize/bin" && chown "65533":"65533" "/srv/dockerize/bin" && mkdir -p "/opt/lib" && chown "65533":"65533" "/opt/lib"
RUN (getent group "900" || groupadd -o -g "900" -r "runuser") && (getent passwd "900" || useradd -l -o -m -d "/home/runuser" -r -g "runuser" -u "900" "runuser")
USER 65533
ENV HOME="/home/somebody"
WORKDIR "/srv/dockerize/bin"
ENV DJANGO_SETTINGS_MODULE="toolhub.settings" DOCKERIZE_VERSION="v0.6.1" PIP_DISABLE_PIP_VERSION_CHECK="on" PIP_NO_CACHE_DIR="off" PYTHONBUFFERED="1" PYTHONDONTWRITEBYTECODE="1"
RUN /bin/bash "-c" "wget --no-verbose https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz && tar -C /srv/dockerize/bin -xzvf dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz && rm dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz"
USER 900
ENV HOME="/home/runuser"

FROM docker-registry.wikimedia.org/python3-buster:latest AS local-python
USER 0
ENV HOME="/root"
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && apt-get install -y "build-essential" "default-libmysqlclient-dev" "gettext" "git" "python3-dev" "python3-venv" && rm -rf /var/lib/apt/lists/*
RUN python3 "-m" "easy_install" "pip" && python3 "-m" "pip" "install" "-U" "setuptools" "wheel" "tox" "pip"
ENV POETRY_VIRTUALENVS_PATH="/opt/lib/poetry"
RUN python3 "-m" "pip" "install" "-U" "poetry==1.1.7"
RUN (getent group "65533" || groupadd -o -g "65533" -r "somebody") && (getent passwd "65533" || useradd -l -o -m -d "/home/somebody" -r -g "somebody" -u "65533" "somebody") && mkdir -p "/srv/app" && chown "65533":"65533" "/srv/app" && mkdir -p "/opt/lib" && chown "65533":"65533" "/opt/lib"
RUN (getent group "900" || groupadd -o -g "900" -r "runuser") && (getent passwd "900" || useradd -l -o -m -d "/home/runuser" -r -g "runuser" -u "900" "runuser")
USER 65533
ENV HOME="/home/somebody"
WORKDIR "/srv/app"
ENV DJANGO_SETTINGS_MODULE="toolhub.settings" PIP_DISABLE_PIP_VERSION_CHECK="on" PIP_NO_CACHE_DIR="off" PYTHONBUFFERED="1" PYTHONDONTWRITEBYTECODE="1"
COPY --chown=65533:65533 ["pyproject.toml", "poetry.lock", "./"]
RUN mkdir -p "/opt/lib/poetry"
RUN poetry "install" "--no-root"
COPY --chown=65533:65533 [".", "."]
COPY --chown=65533:65533 --from=dockerize ["/srv/dockerize", "/srv/dockerize"]

LABEL blubber.variant="local-python" blubber.version="0.8.0+a6bf87e"
