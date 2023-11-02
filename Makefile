.PHONY: build

build:
	$(eval VERSION := $(shell cat VERSION.txt))
	docker build -t itsankoff/gopro:$(VERSION) .
	docker push itsankoff/gopro:$(VERSION)
