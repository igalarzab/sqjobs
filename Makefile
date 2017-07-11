.PHONY: default help deps base build stop test shell

export SERVICE_NAME := sqjobs

BUILD_ENV ?= dev

HISTORY_FILE := ~/.bash_history.$(SERVICE_NAME)

# Required for the `deps` task
SHELL := $(shell which bash)

DOCKER := $(shell command -v docker)

COMPOSE := $(shell command -v docker-compose)

COMPOSE_ENV := $(COMPOSE) -f build/$(BUILD_ENV)/docker-compose.yml

COMPOSE_CMD := $(COMPOSE_ENV) run --rm $(SERVICE_NAME)

DATA_DIR := ~/.tktdata/$(SERVICE_NAME)

# Get the main unix group for the user running make (to be used later)
export GID := $(shell id -g)
# Get the unix user id for the user running make (to be used later)
export UID := $(shell id -u)

help:
	@more Makefile

deps:
ifndef DOCKER
	@echo "Docker is not available. Please install docker"
	@exit 1
endif
ifndef COMPOSE
	@echo "docker-compose is not available. Please install docker-compose"
	@exit 1
endif
	@touch $(HISTORY_FILE)
	mkdir -p $(DATA_DIR)

base: deps
	$(COMPOSE) -f build/base/docker-compose.yml build

build: base
	$(COMPOSE_ENV) build

stop:
	$(COMPOSE_ENV) stop
	$(COMPOSE_ENV) rm -f -v

shell: build
	$(COMPOSE_CMD) /bin/bash

test: build
	set -o pipefail; \
	$(COMPOSE_CMD) pytest
