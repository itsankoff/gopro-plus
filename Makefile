.PHONY: help, docker, release

help:
	@echo "Makefile for managing Docker container and image builds for the GoPro project."
	@echo
	@echo "Usage: make <target>"
	@echo
	@echo "Targets:"
	@echo "  run          Run the Docker container with the specified environment variables."
	@echo "  stop         Stop the Docker container (if running)."
	@echo "  logs         Tail logs from the Docker container."
	@echo "  clean        Stop and remove the Docker container."
	@echo "  docker       Build the Docker image for the current platform."
	@echo "  release      Build and push the multi-platform Docker image."
	@echo
	@echo "Environment Variables:"
	@echo "  ACTION        Action to perform inside the container (default: 'download')."
	@echo "  PAGES         Number of pages to process (default: 1)."
	@echo "  PER_PAGE      Number of items per page (default: 2)."
	@echo "  DOWNLOAD_PATH Path to store downloaded data (default: './download')."
	@echo "  AUTH_TOKEN    Authentication token (must be set in the environment)."
	@echo "  CONTAINER_NAME Name of the Docker container (default: 'gopro')."
	@echo "  BUILD_PLATFORMS Platforms to build for in the 'release' target (default: 'linux/amd64,linux/arm64,linux/arm/v7')."
	@echo
	@echo "Docker Image Configuration:"
	@echo "  IMAGE         Base image name (default: 'itsankoff/gopro')."
	@echo "  VERSION       Version tag (read from VERSION.txt)."
	@echo "  IMAGE_WITH_VERSION Full image name with version tag ('IMAGE:VERSION')."
	@echo
	@echo "Examples:"
	@echo "  make run"
	@echo "  make release"

# Docker default environment
ACTION ?= download
PAGES ?= 1
PER_PAGE ?= 2
DOWNLOAD_PATH ?= ./download
AUTH_TOKEN := $(shell echo $$AUTH_TOKEN)
USER_ID := $(shell echo $$USER_ID)

# Docker container
CONTAINER_NAME ?= gopro

# Docker image
BUILD_PLATFORMS ?= linux/amd64,linux/arm64,linux/arm/v7
IMAGE := itsankoff/gopro
VERSION := $(shell cat VERSION.txt)
IMAGE_WITH_VERSION = $(IMAGE):$(VERSION)

run: clean
	@docker run -d --name $(CONTAINER_NAME) \
		-v ./download:/app/download \
		-e AUTH_TOKEN=$(AUTH_TOKEN) \
		-e USER_ID=$(USER_ID) \
		-e ACTION=$(ACTION) \
		-e PAGES=$(PAGES) \
		-e PER_PAGE=$(PER_PAGE) \
		-e DOWNLOAD_PATH=$(DOWNLOAD_PATH) \
		$(IMAGE_WITH_VERSION)

stop:
	@docker stop $(CONTAINER_NAME) || true

logs:
	@docker logs -f $(CONTAINER_NAME)

clean: stop
	@docker rm $(CONTAINER_NAME) || true

docker:
	@docker build -t $(IMAGE_WITH_VERSION) .

release:
	@docker buildx build --platform $(BUILD_PLATFORMS) -t $(IMAGE_WITH_VERSION) -t $(IMAGE):latest --push .

