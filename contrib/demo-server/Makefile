# Copyright (c) 2021 Wikimedia Foundation and contributors.
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

IMAGE := docker-registry.wikimedia.org/wikimedia/wikimedia-toolhub:latest

help:
	@echo "Make targets:"
	@echo "============="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'
.PHONY: help

start: ## Start the docker-compose stack
	sudo systemctl start toolhub.service
.PHONY: start

stop:  ## Stop the docker-compose stack
	sudo systemctl stop toolhub.service
.PHONY: stop

restart: ## Restart the docker-compose stack
	sudo systemctl restart toolhub.service
.PHONY: restart

status: ## Show status of the docker-compose stack
	sudo systemctl status toolhub.service --no-pager --full || /bin/true
	docker-compose ps
.PHONY: status

pull: ## Pull the latest image down from the docker repo
	sudo docker pull ${IMAGE}
.PHONY: pull

update: pull restart ## Update and restart
.PHONY: update

web-shell:  ## Get an interactive shell inside the web container
	docker-compose exec web bash
.PHONY: web-shell

db-shell:  ## Get an interactive shell inside the db container
	docker-compose exec db bash
.PHONY: db-shell

search-shell:  ## Get an interactive shell inside the search container
	docker-compose exec search bash
.PHONY: search-shell

tail:  ## Tail logs from the docker-compose stack
	docker-compose logs -f
.PHONY: tail

migrate: ## Run `manage.py migrate`
	docker-compose exec web \
		poetry run python3 manage.py migrate
.PHONY: migrate

createinitialrevisions: ## Run `manage.py createinitialrevisions`
	docker-compose exec web \
		poetry run python3 manage.py createinitialrevisions
.PHONY: createinitialrevisions

index: ## Create and populate search index
	docker-compose exec web \
		poetry run python3 manage.py search_index --rebuild -f
.PHONY: index

clean:  ## Clean up Docker images and containers
	yes | docker image prune
	yes | docker container prune
.PHONY: clean

destroy: clean  ## Clean up Docker images, containers, and volumes
	yes | docker volume rm demo_dbdata
	yes | docker volume rm demo_esdata
.PHONY: destroy
