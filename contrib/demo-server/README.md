Toolhub demo server setup
=========================

Manual setup instructions follow. Someday™ this could be turned into a more
automated process, but not today. ;)

* Create instance via Horizon
* Create cinder volume via Horizon
* Mount cinder volume at /srv
* Install docker-ce using upstream packages and docs:
  <https://docs.docker.com/engine/install/debian/>
* Move Docker storage dir to /srv/docker using process from
  <https://www.guguweb.com/2019/02/07/how-to-move-docker-data-directory-to-another-location-on-ubuntu/>
* Configure Docker to log to journald:
  <https://docs.docker.com/config/containers/logging/configure/>
* Install docker-compose using pip3
* (optional) Add yourself to the `docker` user group so that playing with
  docker from the cli is easier (removes need for `sudo`).
