-include .env

DOCKER := docker compose
ROOT_DIR := $(shell pwd)
PROFILES := --profile servercontroller

ifdef DISCORD_TOKEN
    PROFILES += --profile discord
endif
ifdef TS_AUTHKEY
    PROFILES += --profile tailscale
endif

.PHONY: build
build:
		@echo "Services that will be started:"
		@echo "servercontroller: always"
		@echo "discord: $(if $(DISCORD_TOKEN),yes,no)"
		@echo "tailscale: $(if $(TS_AUTHKEY),yes,no)"
		$(DOCKER) $(PROFILES) build

.PHONY: run
run:
		@echo "Services that will be running:"
		@echo "servercontroller: always"
		@echo "discord: $(if $(DISCORD_TOKEN),yes,no)"
		@echo "tailscale: $(if $(TS_AUTHKEY),yes,no)"
		$(DOCKER) $(PROFILES) up -d