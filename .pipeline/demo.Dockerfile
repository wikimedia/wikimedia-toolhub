# Dockerfile for *local development*.
# Generated by Blubber from .pipeline/blubber.yaml
FROM docker-registry.wikimedia.org/nodejs10-devel AS prep-nodejs
USER 0
ENV HOME="/root"
RUN (getent group "65533" || groupadd -o -g "65533" -r "somebody") && (getent passwd "65533" || useradd -l -o -m -d "/home/somebody" -r -g "somebody" -u "65533" "somebody") && mkdir -p "/srv/app" && chown "65533":"65533" "/srv/app" && mkdir -p "/opt/lib" && chown "65533":"65533" "/opt/lib"
RUN (getent group "900" || groupadd -o -g "900" -r "runuser") && (getent passwd "900" || useradd -l -o -m -d "/home/runuser" -r -g "runuser" -u "900" "runuser")
USER 65533
ENV HOME="/home/somebody"
WORKDIR "/srv/app"
ENV DJANGO_SETTINGS_MODULE="toolhub.settings" PIP_DISABLE_PIP_VERSION_CHECK="on" PIP_NO_CACHE_DIR="off" PYTHONBUFFERED="1" PYTHONDONTWRITEBYTECODE="1"
COPY --chown=65533:65533 ["package.json", "package-lock.json", "./"]
RUN npm install
COPY --chown=65533:65533 ["vue.config.js", "./"]
COPY --chown=65533:65533 ["vue/", "vue/"]
COPY --chown=65533:65533 [".git/", ".git/"]
RUN /bin/bash "-c" "ls -alh && npm run-script build:vue"
USER 900
ENV HOME="/home/runuser"
ENV NODE_ENV="development"

FROM docker-registry.wikimedia.org/python3-buster:latest AS prep
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
ENV DJANGO_SECRET_KEY="FAKE_SECRET_FOR_PREP_BUILD" DJANGO_SETTINGS_MODULE="toolhub.settings" PIP_DISABLE_PIP_VERSION_CHECK="on" PIP_NO_CACHE_DIR="off" PYTHONBUFFERED="1" PYTHONDONTWRITEBYTECODE="1" WIKIMEDIA_OAUTH2_KEY="FAKE_KEY_FOR_PREP_BUILD" WIKIMEDIA_OAUTH2_SECRET="FAKE_TOKEN_FOR_PREP_BUILD"
COPY --chown=65533:65533 ["pyproject.toml", "poetry.lock", "./"]
RUN mkdir -p "/opt/lib/poetry"
RUN poetry "install" "--no-root" "--no-dev"
COPY --chown=65533:65533 ["./", "./"]
COPY --chown=65533:65533 --from=prep-nodejs ["/srv/app/vue/dist", "vue/dist/"]
RUN /bin/bash "-c" "ls -alh && poetry run ./manage.py collectstatic -c --no-input && poetry run python3 -mjson.tool staticfiles/staticfiles.json > /tmp/staticfiles.json && mv /tmp/staticfiles.json staticfiles/staticfiles.json && poetry run ./manage.py compilemessages"
USER 900
ENV HOME="/home/runuser"

FROM docker-registry.wikimedia.org/python3-buster:latest AS demo
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
ENV DB_NAME="/dev/shm/toolhub.sqlite3" DJANGO_SETTINGS_MODULE="toolhub.settings" PIP_DISABLE_PIP_VERSION_CHECK="on" PIP_NO_CACHE_DIR="off" PYTHONBUFFERED="1" PYTHONDONTWRITEBYTECODE="1"
COPY --chown=65533:65533 ["pyproject.toml", "poetry.lock", "./"]
RUN mkdir -p "/opt/lib/poetry"
RUN poetry "install" "--no-root" "--no-dev"
COPY --chown=65533:65533 --from=prep ["/srv/app", "."]
USER 900
ENV HOME="/home/runuser"
ENTRYPOINT ["/bin/bash", "-c", "poetry run python3 manage.py migrate && poetry run python3 manage.py createinitialrevisions && poetry run python3 manage.py loaddata toolhub/fixtures/demo.yaml && poetry run python3 manage.py crawl && poetry run python3 manage.py runserver --noreload --nostatic 0.0.0.0:8000"]

LABEL blubber.variant="demo" blubber.version="0.8.0+459234d"
