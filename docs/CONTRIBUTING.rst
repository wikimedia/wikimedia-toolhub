#################
How to contribute
#################

This document provides guidelines for people who want to contribute to the
Toolhub project.


***********************
Development environment
***********************

Dependencies
============
The following software will need to be installed on your local development
machine:

- Git_
- Curl_
- `Docker and Docker Compose`_
- `GNU Make`_

Getting started
===============
Toolhub's development environment is designed to allow you to test and run
everything from inside of a collection of Docker containers managed with
Docker Compose. The git repo contains a Makefile in its root directory that
should make working with `docker-compose` easier.

.. highlight:: shell-session

::

   $ git clone https://gerrit.wikimedia.org/r/wikimedia/toolhub
   $ cd toolhub
   $ make init
   $ make test


Try running `make help` to see more make targets that you may find useful.

Once you have the development environment setup, you can navigate to
http://localhost:8000/ to see the Toolhub web interface.

Running the crawler
===================
First, you need to open an interactive shell session inside the web container.
You can do this by running ``make web-shell``. Now, run the following commands
to populate the database with urls and run the crawler:

.. highlight:: shell-session

::

    $ poetry run python3 manage.py loaddata toolhub/fixtures/demo.yaml
    $ poetry run python3 manage.py crawl --quiet

Configuration
=============
Toolhub follows the `twelve-factor app`_ pattern of storing deployment
variable configuration in the environment. The docker-compose.yaml file lists
all of the environment variables that can be set to change your local
configuration. The ``make init`` step will generate a .env file for you to start
from. This file will be automatically used by docker-compose to populate the
environment for your local containers.

If you are having issues that you suspect might be related to the environment
variable configuration, one possible solution might be to delete the .env file
as well as the existing containers and volumes before running ``make init``
again.

NOTE: These commands will remove ALL of your unused local containers
and volumes. If you have other containers or volumes that you want to keep,
check out the `Docker and Docker Compose`_ documentation for more information.

.. highlight:: shell-session

::

    $ make stop
    $ rm .env
    $ docker system prune && docker volume prune
    $ make init


.. _Git: https://git-scm.com/
.. _Curl: https://curl.haxx.se/
.. _`Docker and Docker Compose`: https://www.docker.com/
.. _`GNU Make`: https://www.gnu.org/software/make/
.. _`twelve-factor app`: https://12factor.net/
