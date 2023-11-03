.PHONY: build, push

CONTAINER_NAME ?= gopro
ACTION ?= download
PAGES ?= 1
PER_PAGE ?= 2
DOWNLOAD_PATH ?= ./download

IMAGE := itsankoff/gopro
VERSION := $(shell cat VERSION.txt)
IMAGE_WITH_VERSION = $(IMAGE):$(VERSION)
AUTH_TOKEN := $(shell echo $$AUTH_TOKEN)

build:
	@docker build -t $(IMAGE_WITH_VERSION) .

push:
	@docker push $(IMAGE_WITH_VERSION)

run: clean
	@docker run -d --name $(CONTAINER_NAME) \
		-v ./download:/app/download \
		-e AUTH_TOKEN=$(AUTH_TOKEN) \
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
