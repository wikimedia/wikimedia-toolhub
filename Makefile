# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free software: you can redistribute it and/or modify
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

this := $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
PROJECT_DIR := $(dir $(this))
PIPELINE_DIR := $(PROJECT_DIR)/.pipeline
BLUBBEROID := https://blubberoid.wikimedia.org
DOCKERIZE := /srv/dockerize/bin/dockerize
DOCKERFILES := $(PIPELINE_DIR)/local-python.Dockerfile $(PIPELINE_DIR)/dev-nodejs.Dockerfile
DEMO_DOCKERFILE := $(PIPELINE_DIR)/local-python.Dockerfile
DEMO_TAG := bd808/toolhub-beta:latest
DEFAULT_CONTAINERS := web db nodejs
ALL_TESTS := test-python test-nodejs-lint test-nodejs-unit

help:
	@echo "Make targets:"
	@echo "============="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'
.PHONY: help

start: .env $(DOCKERFILES) ## Start the docker-compose stack
	docker-compose up --build --detach ${DEFAULT_CONTAINERS}
.PHONY: start

stop:  ## Stop the docker-compose stack
	docker-compose stop
.PHONY: stop

restart: stop start  ## Restart the docker-compose stack
.PHONY: restart

status:  ## Show status of the docker-compose stack
	docker-compose ps
.PHONY: status

web-shell:  ## Get an interactive shell inside the web container
	docker-compose exec web bash
.PHONY: web-shell

nodejs-shell:  ## Get an interactive shell inside the nodejs container
	docker-compose exec nodejs bash
.PHONY: nodejs-shell

db-shell:  ## Get an interactive shell inside the db container
	docker-compose exec db bash
.PHONY: db-shell

tail:  ## Tail logs from the docker-compose stack
	docker-compose logs -f
.PHONY: tail

migrate: ## Run `manage.py migrate`
	docker-compose exec web $(DOCKERIZE) -wait tcp://db:3306 \
		poetry run python3 manage.py migrate
.PHONY: migrate

make-admin-user:
	docker-compose exec web  $(DOCKERIZE) -wait tcp://db:3306 sh -c " \
		poetry run python3 manage.py shell -c \"import os; from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@localhost', os.environ['DJANGO_SUPERUSER_PASSWORD']);\" \
	"
.PHONY: make-admin-user

init: start migrate make-admin-user  ## Initialize docker-compose stack
.PHONY: init

test: $(ALL_TESTS) ## Run tests inside the docker-compose stack
.PHONY: test

test-python: test-python-lint test-python-unit
.PHONY: test-python

test-python-lint:  ## Run linter checks for Python code
	@echo "== Lint Python =="
	docker-compose exec web sh -c " \
		poetry check \
		&& poetry run flakehell lint \
		&& poetry run black --check --diff . \
		&& poetry run bandit -ii -r toolhub/ \
	"
.PHONY: test-python-lint

test-python-unit:  ## Run unit tests for Python code
	@echo "== Test Python =="
	docker-compose exec web sh -c " \
		export DJANGO_SECRET_KEY='this is not really a secret'; \
		export DB_ENGINE='django.db.backends.sqlite3'; \
		export DB_NAME=':memory:'; \
		poetry run coverage erase \
		&& poetry run coverage run --branch manage.py test \
		&& poetry run coverage report \
	"
.PHONY: test-python-unit

test-nodejs: test-nodejs-lint test-nodejs-unit
.PHONY: test-nodejs

test-nodejs-lint:  ## Run linter checks for nodejs code
	@echo "== Lint Nodejs =="
	docker-compose exec nodejs npm run-script lint
.PHONY: test-nodejs-lint

test-nodejs-unit:  ## Run unit tests for nodejs code
	@echo "== Test Nodejs =="
	docker-compose exec nodejs npm run-script test
.PHONY: test-nodejs-unit

schemas:  ## Create/update versioned json schema documents
	docker-compose exec nodejs npm run-script schemas:generate
.PHONY: schemas

messages:  ## Create/update translatable messages
	@echo "== Make messages =="
	docker-compose exec web sh -c " \
		poetry run ./manage.py makemessages -l en -i node_modules \
		&& poetry run ./manage.py compilemessages \
	"
.PHONY: messages

docs:  ## Build sphinx docs
	docker-compose exec web sh -c " \
		poetry run sphinx-apidoc -f -o docs/source toolhub \
		&& rm docs/source/modules.rst \
		&& poetry run sphinx-build -W -b html docs/ docs/_build/html \
	"
.PHONY: docs

artifacts: schemas messages docs  ## Generate code & doc artifacts
.PHONY: artifacts

format-code:  ## Reformat Python and JS files
	docker-compose exec web poetry run black .
	docker-compose exec nodejs npm run-script format
.PHONY: format-code

clean:  ## Clean up Docker images and containers
	yes | docker image prune
	yes | docker container prune
.PHONY: clean

destroy: clean  ## Clean up Docker images, containers, and volumes
	yes | docker volume rm toolhub_dbdata
.PHONY: destroy

demo: $(DEMO_DOCKERFILE)
	docker build --pull --force-rm=true --file $(DEMO_DOCKERFILE) . -t $(DEMO_TAG)
	docker push $(DEMO_TAG)

.env:  ## Generate a .env file for local development
	./bin/make_env.sh ./.env

%.Dockerfile: $(PIPELINE_DIR)/blubber.yaml
	echo "# Dockerfile for *local development*." > $@
	echo "# Generated by Blubber from .pipeline/blubber.yaml" >> $@
	curl -sH 'content-type: application/yaml' --data-binary @$^ \
	$(BLUBBEROID)/v1/$(*F) >> $@
