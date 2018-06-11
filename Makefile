#.PHONY: build push

VERSION = 1.0.0-beta.4
IMAGE = kapancuti:$(VERSION)


all: build push

build:
	docker build -t $(IMAGE) -f Dockerfile .

push:
	docker push swallowstalker/$(IMAGE)
