# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free oftware: you can redistribute it and/or modify
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

DEFAULT_CONTAINERS = web db

help:
	echo "Make targets:"
	echo "============="
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

start: .env  ## Start the docker-compose stack
	docker-compose up --build --detach ${DEFAULT_CONTAINERS}

stop:  ## Stop the docker-compose stack
	docker-compose stop

restart: stop start  ## Restart the docker-compose stack

status:  ## Show status of the docker-compose stack
	docker-compose ps

web-shell:  ## Get an interactive shell inside the web container
	docker-compose exec web bash

nodejs-shell:  ## Get an interactive shell inside the nodejs container
	docker-compose run --rm nodejs bash

tail:  ## Tail logs from the docker-compose stack
	docker-compose logs -f

migrate: ## Run `manage.py migrate`
	docker-compose exec web dockerize -wait tcp://db:3306 \
		poetry run python3 manage.py migrate

init: start migrate  ## Initialize docker-compose stack

test: export DJANGO_SECRET_KEY = "this is not really a secret"
test: export DB_ENGINE = django.db.backends.sqlite3
test: export DB_NAME = /tmp/db.sqlite3
test:  ## Run tests inside the docker-compose stack
	echo "== Poetry =="
	docker-compose exec web poetry check
	echo "== Flake8 =="
	docker-compose exec web poetry run flakehell lint
	echo "== Black =="
	docker-compose exec web poetry run black --check --diff .
	echo "== manage.py test =="
	docker-compose exec web poetry run coverage erase
	docker-compose exec web poetry run coverage run --branch manage.py test
	docker-compose exec web poetry run coverage report
	echo "== Bandit =="
	docker-compose exec web poetry run bandit -ii -r toolhub/
	echo "== JSON schema =="
	docker-compose run --rm nodejs npm test
	echo "== Building docs =="
	docker-compose exec web poetry run sphinx-build -W -b html docs/ docs/_build/html

docs:
	docker-compose exec web poetry run sphinx-build -W -b html docs/ docs/_build/html

build: Dockerfile  ## Build the Toolhub docker container
	docker build -t 'toolhub:dev' .

clean:  ## Clean up Docker images and containers
	yes | docker image prune
	yes | docker container prune

destroy: clean  ## Clean up Docker images, containers, and volumes
	yes | docker volume rm toolhub_dbdata

.env:  ## Generate a .env file for local development
	./bin/make_env.sh ./.env

.PHONY: help build clean start stop status restart shell tail migrate init test docs
.SILENT: ;
