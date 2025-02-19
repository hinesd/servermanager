ifeq ($(wildcard .env),)
    $(info No .env file found...\ngenerating from .sample-env...)
    $(shell cp .sample-env .env)
    $(info .env file has been created!)
endif

-include .env

DOCKER := docker compose
ROOT_DIR := $(shell pwd)
PROFILES := --profile servercontroller

ifdef DISCORD_TOKEN
    PROFILES += --profile discord
endif
ifdef TAILSCALE_AUTHKEY
    PROFILES += --profile tailscale
endif


.PHONY: build
build: build-validation
		$(DOCKER) $(PROFILES) build

.PHONY: run
run:
		$(DOCKER) $(PROFILES) up -d

.PHONY: stop
stop:
		$(DOCKER) $(PROFILES) down


build-validation:

		@echo "----------------------------------------------------------------"
		@echo "----------------------------------------------------------------"
		@echo "Services that will be built:"
		@echo "servercontroller: always"
		@echo "discord: $(if $(DISCORD_TOKEN),yes,no)"
		@echo "tailscale: $(if $(TAILSCALE_AUTHKEY),yes,no)"
		@echo "----------------------------------------------------------------"
		@echo "----------------------------------------------------------------"

