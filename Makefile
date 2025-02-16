-include .env

$(if [ ! -f .env ], $(shell cp .sample-env .env))

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

		@if [ ! -f server/server.properties ]; then \
			echo "server files dont exist..." && \
			echo "copying server files from sample_files..." && \
			cp sample_files/server.properties server/server.properties && \
			cp sample_files/settings.sh server/settings.sh && \
			cp sample_files/start_script.sh server/start_script.sh && \
			echo "Server files successfully copied"; \
		fi

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

.PHONY: down
down:
		$(DOCKER) $(PROFILES) down