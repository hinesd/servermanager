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
ifdef TS_AUTHKEY
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

		@if [ -n "$(JAVA_INSTALL_SCRIPT)" ] && [ -n "$(JAVA_VERSION)" ]; then \
		    echo "Error: Both JAVA_INSTALL_SCRIPT and JAVA_VERSION are set. Only one should be set at a time."; \
		    exit 1; \
	    elif [ -z "$(JAVA_INSTALL_SCRIPT)" ] && [ -z "$(JAVA_VERSION)" ]; then \
		    echo "Error: Neither JAVA_INSTALL_SCRIPT nor JAVA_VERSION is set. One must be set."; \
		    exit 1; \
	    fi

	    @if [ -n "$(JAVA_INSTALL_SCRIPT)" ]; then \
		    echo "Using Python-only configuration with JAVA_INSTALL_SCRIPT=$(JAVA_INSTALL_SCRIPT)"; \
	    else \
		    echo "Using Java-based configuration with JAVA_VERSION=$(JAVA_VERSION)"; \
	    fi
		@echo "Services that will be started:"
		@echo "servercontroller: always"
		@echo "discord: $(if $(DISCORD_TOKEN),yes,no)"
		@echo "tailscale: $(if $(TS_AUTHKEY),yes,no)"
		@echo "----------------------------------------------------------------"
		@echo "----------------------------------------------------------------"

