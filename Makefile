#.PHONY: build push

VERSION = 1.0.5-beta.3
IMAGE = kapancuti:$(VERSION)


all: build push

build:
	docker build -t $(IMAGE) -f Dockerfile .

push:
	docker login
	docker tag $(IMAGE) swallowstalker/$(IMAGE)
	docker push swallowstalker/$(IMAGE)
