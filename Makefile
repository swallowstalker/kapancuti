#.PHONY: build push

VERSION = 1.0.4
IMAGE = kapancuti:$(VERSION)


all: build push

build:
	docker build -t $(IMAGE) -f Dockerfile .

push:
	echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
	docker tag $(IMAGE) swallowstalker/$(IMAGE)
	docker push swallowstalker/$(IMAGE)
