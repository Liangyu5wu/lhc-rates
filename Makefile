# Every command runs inside the container, through compose.
# `make` (or `make help`) lists the targets.

COMPOSE_PROJECT_NAME := $(shell basename "$(CURDIR)" | tr 'A-Z' 'a-z')
HOST_UID := $(shell id -u)
HOST_GID := $(shell id -g)
export COMPOSE_PROJECT_NAME HOST_UID HOST_GID

# .env holds plain KEY=value lines; include and export them for compose.
ifneq (,$(wildcard .env))
include .env
export $(shell grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | cut -d= -f1)
endif

COMPOSE := docker compose -f docker/compose.yaml
RUN     := $(COMPOSE) run --rm --no-deps -T

.DEFAULT_GOAL := help
.PHONY: help build up down verify clean test lint fmt smoke logs shell lock

##@ Everyday

help: ## List the targets
	@awk 'BEGIN {FS = ":.*## "} /^##@/ {printf "\n%s\n", substr($$0, 5)} /^[a-z-]+:.*## / {printf "  %-8s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the image from docker/uv.lock and docker/package-lock.json
	$(COMPOSE) build app

up: ## Start the app on http://127.0.0.1:8000
	$(COMPOSE) up -d app
	@echo "Open http://127.0.0.1:8000"

down: ## Stop the app
	$(COMPOSE) down

verify: lint test smoke ## Check it all works: lint, test, smoke

clean: ## Back to a fresh clone: this project's containers, images and caches go
	$(COMPOSE) --profile tools down --rmi local --remove-orphans
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +

##@ While developing

test: ## Run the tests
	$(RUN) app python -m pytest -q

lint: ## Check the code, changing nothing
	$(RUN) app ruff check src tests
	$(RUN) app ruff format --check src tests

fmt: ## Rewrite the code into the standard format
	$(RUN) app ruff format src tests
	$(RUN) app ruff check --fix src tests

smoke: ## Start the app, check a real API result, stop it
	$(COMPOSE) up -d app
	$(COMPOSE) exec -T app python -m app.smoke; status=$$?; $(COMPOSE) down; exit $$status

logs: ## Follow the app's output
	$(COMPOSE) logs -f app

shell: ## Open a shell in the container, repository at /work
	$(COMPOSE) run --rm --no-deps app bash

##@ Only when dependencies change

lock: ## Record exact versions in docker/uv.lock and docker/package-lock.json
	$(COMPOSE) --profile tools build lock-py lock-js
	$(RUN) lock-py
	$(RUN) lock-js
