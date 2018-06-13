#.PHONY: build push

VERSION = 1.0.2
IMAGE = kapancuti:$(VERSION)


all: build push

build:
	docker build -t $(IMAGE) -f Dockerfile .

push:
	docker tag $(IMAGE) swallowstalker/$(IMAGE)
	docker push swallowstalker/$(IMAGE)
