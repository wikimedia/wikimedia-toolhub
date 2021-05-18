# Dockerfile for *local development*.
# Generated by Blubber from .pipeline/blubber.yaml
FROM docker-registry.wikimedia.org/nodejs10-devel AS dev-nodejs
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
COPY --chown=65533:65533 [".", "."]
ENV NODE_ENV="development"

LABEL blubber.variant="dev-nodejs" blubber.version="0.8.0+459234d"
