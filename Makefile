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
DOCKERIZE := /srv/dockerize/bin/dockerize
VOLUMES := toolhub_dbdata toolhub_esdata
ALL_TESTS := test-python test-nodejs

# Read envvars file if present
-include $(PROJECT_DIR)/.env

# Set defaults for variables potentially initialized by envvars file
DOCS_HTTP_PORT ?= 8080
# Prefer Compose v2, but allow override on hosts that only have v1
COMPOSE ?= docker compose

help:
	@echo "Make targets:"
	@echo "============="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'
.PHONY: help

start: .env  ## Start the docker-compose stack
	DOCKER_DEFAULT_PLATFORM=linux/amd64 $(COMPOSE) up --build --detach
.PHONY: start

stop:  ## Stop the docker-compose stack
	$(COMPOSE) stop
.PHONY: stop

restart: stop start  ## Restart the docker-compose stack
.PHONY: restart

status:  ## Show status of the docker-compose stack
	$(COMPOSE) ps
.PHONY: status

web-shell:  ## Get an interactive shell inside the web container
	$(COMPOSE) exec web bash
.PHONY: web-shell

nodejs-shell:  ## Get an interactive shell inside the nodejs container
	$(COMPOSE) exec nodejs bash
.PHONY: nodejs-shell

db-shell:  ## Get an interactive shell inside the db container
	grep DOCKER_DB_MYSQL_ROOT_PASSWORD .env
	$(COMPOSE) exec db bash
.PHONY: db-shell

search-shell:  ## Get an interactive shell inside the search container
	$(COMPOSE) exec search bash
.PHONY: search-shell

oauth-client: .env  ## Start the oauth-client app container in the foreground
	$(COMPOSE) \
		--file docker-compose.yaml \
		--file contrib/oauth-client-example/docker-compose.oauth.yaml \
		up --build oauth-client
.PHONY: oauth-client

prometheus:  ## Start the prometheus monitoring container
	$(COMPOSE) \
		--file docker-compose.yaml \
		--file contrib/prometheus/docker-compose.prometheus.yaml \
		up --detach prometheus
.PHONY: prometheus

prometheus-shell: prometheus  ## Get an interactive shell inside the prometheus container
	$(COMPOSE) \
		--file docker-compose.yaml \
		--file contrib/prometheus/docker-compose.prometheus.yaml \
		exec prometheus sh
.PHONY: prometheus-shell

tail:  ## Tail logs from the docker-compose stack
	$(COMPOSE) logs --follow
.PHONY: tail

migrate: ## Run `manage.py migrate`
	$(COMPOSE) exec web $(DOCKERIZE) -wait tcp://db:3306 \
		poetry run python3 manage.py migrate
.PHONY: migrate

createinitialrevisions: ## Run `manage.py createinitialrevisions`
	$(COMPOSE) exec web $(DOCKERIZE) -wait tcp://db:3306 \
		poetry run python3 manage.py createinitialrevisions
.PHONY: createinitialrevisions

index: ## Create and populate search index
	$(COMPOSE) exec web $(DOCKERIZE) \
		-wait tcp://db:3306 -wait tcp://search:9200 \
		poetry run python3 manage.py search_index --rebuild -f
.PHONY: index

crawl: ## Run crawler
	$(COMPOSE) exec web $(DOCKERIZE) \
		-wait tcp://db:3306 -wait tcp://search:9200 \
		poetry run python3 manage.py crawl --quiet
.PHONY: crawl

make-admin-user:
	$(COMPOSE) exec web  $(DOCKERIZE) -wait tcp://db:3306 sh -c " \
		poetry run python3 manage.py shell -c \"import os; from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@localhost', os.environ['DJANGO_SUPERUSER_PASSWORD']);\" \
	"
.PHONY: make-admin-user

init: start migrate createinitialrevisions make-admin-user  ## Initialize docker-compose stack
.PHONY: init

test: $(ALL_TESTS) ## Run tests inside the docker-compose stack
.PHONY: test

test-python: test-python-lint test-python-unit
.PHONY: test-python

test-python-lint:  ## Run linter checks for Python code
	@echo "== Lint Python =="
	$(COMPOSE) exec web sh -c " \
		export HOME=/tmp/runtime-home; \
		poetry check \
		&& poetry run flake8 \
		&& poetry run black --check --diff . \
		&& poetry run bandit -ii -r toolhub/ \
	"
.PHONY: test-python-lint

test-python-unit:  ## Run unit tests for Python code
	@echo "== Test Python =="
	$(COMPOSE) exec web sh -c " \
		export HOME=/tmp/runtime-home; \
		export DJANGO_SECRET_KEY='this is not really a secret'; \
		export DB_ENGINE='django.db.backends.sqlite3'; \
		export DB_NAME=':memory:'; \
		export ES_DSL_AUTOSYNC=0; \
		export STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage'; \
		poetry run coverage erase \
		&& poetry run coverage run --branch manage.py test \
		&& poetry run coverage report \
	"
.PHONY: test-python-unit

test-nodejs: test-nodejs-lint test-nodejs-unit
.PHONY: test-nodejs

test-nodejs-lint:  ## Run linter checks for nodejs code
	@echo "== Lint Nodejs =="
	$(COMPOSE) exec nodejs sh -c " \
		export HOME=/tmp/runtime-home; \
		npm run-script lint \
	"
.PHONY: test-nodejs-lint

test-nodejs-unit:  ## Run unit tests for nodejs code
	@echo "== Test Nodejs =="
	$(COMPOSE) exec nodejs sh -c " \
		export HOME=/tmp/runtime-home; \
		npm run-script unit \
	"
.PHONY: test-nodejs-unit

schemas:  ## Create/update versioned json schema documents
	$(COMPOSE) exec nodejs npm run-script schemas:generate
.PHONY: schemas

messages:  ## Create/update translatable messages
	@echo "== Make messages =="
	$(COMPOSE) exec web sh -c " \
		poetry run ./manage.py makemessages -l en -i node_modules \
		&& poetry run ./manage.py compilemessages --exclude qqq \
	"
.PHONY: messages

docs:  ## Build sphinx docs
	$(COMPOSE) exec web sh -c " \
		poetry run sphinx-apidoc -f -o docs/source toolhub \
		&& rm docs/source/modules.rst \
		&& poetry run sphinx-build -b html docs/ docs/_build/html \
	"
.PHONY: docs

serve-docs:  ## Live-serve sphinx docs
	@echo "View sphinx docs at http://localhost:${DOCS_HTTP_PORT}/"
	$(COMPOSE) exec web sh -c " \
		poetry run sphinx-autobuild -b \
		html --host 0.0.0.0 --port 8080 docs docs/_build/html \
	"
.PHONY: serve-docs

artifacts: schemas messages docs  ## Generate code & doc artifacts
.PHONY: artifacts

format-code:  ## Reformat Python and JS files
	$(COMPOSE) exec web poetry run black .
	$(COMPOSE) exec nodejs npm run-script format
.PHONY: format-code

generate-spdx:  ## Generate a new SPDX data file
	$(COMPOSE) exec web sh -c " \
		poetry run python3 toolhub/apps/toolinfo/generate_spdx.py > \
			toolhub/apps/toolinfo/spdx.py && \
		poetry run black toolhub/apps/toolinfo/spdx.py && \
		cat toolhub/apps/toolinfo/spdx.py \
	"
.PHONY: generate-spdx

clean:  ## Clean up Docker images and containers
	yes | docker image prune
	yes | docker container prune
.PHONY: clean

destroy: clean  ## Clean up Docker images, containers, and volumes
	yes | docker volume rm $(VOLUMES)
.PHONY: destroy

.env:  ## Generate a .env file for local development
	./bin/make_env.sh ./.env
