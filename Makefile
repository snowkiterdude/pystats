# ==============================================================================
# pystats - Container Build System
#
# Builds a single multi-architecture (amd64 + arm64) image and pushes it to
# Docker Hub as one manifest. Run `make help` to see all available targets.
#
# Docker credentials are read from ~/.docker/skd_docker_io_creds (YAML).
# See BUILDING.md for the expected format of that file.
# ==============================================================================

DOCKER_CREDS   := $(HOME)/.docker/skd_docker_io_creds
DOCKER_USER    := $(shell grep '^username:' $(DOCKER_CREDS) 2>/dev/null | awk '{print $$2}')
DOCKER_TOKEN   := $(shell grep '^token:'    $(DOCKER_CREDS) 2>/dev/null | awk '{print $$2}')

IMAGE_NAME     := snowkiterdude/pystats
VERSION        := v0.0.4
PLATFORMS      := linux/amd64,linux/arm64
BUILDER_NAME   := pystats-builder
CONTAINER_NAME := pystats
VOLUME_NAME    := pystats-data
PORT           := 8080

.DEFAULT_GOAL := help

.PHONY: help builder build build-local run-local push release inspect login clean clean-data

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

login: ## Authenticate to docker.io using ~/.docker/skd_docker_io_creds
	@test -f $(DOCKER_CREDS) || \
		(echo "ERROR: credentials file not found: $(DOCKER_CREDS)"; exit 1)
	@test -n "$(DOCKER_USER)"  || \
		(echo "ERROR: 'username' not found in $(DOCKER_CREDS)"; exit 1)
	@test -n "$(DOCKER_TOKEN)" || \
		(echo "ERROR: 'token' not found in $(DOCKER_CREDS)"; exit 1)
	@echo "$(DOCKER_TOKEN)" | docker login docker.io -u $(DOCKER_USER) --password-stdin

builder: ## Create (or reuse) a buildx builder capable of multi-arch builds
	@docker buildx inspect $(BUILDER_NAME) >/dev/null 2>&1 || \
		docker buildx create --name $(BUILDER_NAME) --driver docker-container --bootstrap
	@docker buildx use $(BUILDER_NAME)

build-local: builder ## Build for your current machine only and load into local docker (fast, for testing)
	docker buildx build \
		--builder $(BUILDER_NAME) \
		--tag $(IMAGE_NAME):$(VERSION) \
		--tag $(IMAGE_NAME):latest \
		--load \
		.

run-local: ## Stop any running pystats container, then start a fresh one from the local image
	-docker rm -f $(CONTAINER_NAME) 2>/dev/null
	@docker volume inspect $(VOLUME_NAME) >/dev/null 2>&1 || \
		docker volume create $(VOLUME_NAME)
	docker run -d \
		--name $(CONTAINER_NAME) \
		--restart unless-stopped \
		-p $(PORT):$(PORT) \
		-v $(VOLUME_NAME):/var/lib/pystats \
		$(IMAGE_NAME):latest
	@echo ""
	@echo "pystats running → http://localhost:$(PORT)"

build: login builder ## Authenticate, then build amd64+arm64 and push a multi-arch manifest
	docker buildx build \
		--builder $(BUILDER_NAME) \
		--platform $(PLATFORMS) \
		--tag $(IMAGE_NAME):$(VERSION) \
		--tag $(IMAGE_NAME):latest \
		--push \
		.

push: build ## Alias for `build` (multi-arch builds push as part of the build step)

release: ## Tag the current commit with VERSION, then build and push the multi-arch image
	git tag -a $(VERSION) -m "Release $(VERSION)"
	git push origin $(VERSION)
	$(MAKE) build

inspect: ## Verify the pushed image actually contains both architectures
	docker buildx imagetools inspect $(IMAGE_NAME):$(VERSION)

clean: ## Remove the buildx builder, stop local container, and prune dangling images
	-docker rm -f $(CONTAINER_NAME) 2>/dev/null
	-docker buildx rm $(BUILDER_NAME)
	-docker image prune -f

clean-data: ## WARNING: permanently delete the pystats sqlite volume
	-docker rm -f $(CONTAINER_NAME) 2>/dev/null
	-docker volume rm $(VOLUME_NAME)
