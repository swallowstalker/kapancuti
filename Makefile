#.PHONY: test build push

VERSION = 2.0.2
IMAGE = swallowstalker/kapancuti:$(VERSION)

BASE_VERSION = 1.0.0
BASE_IMAGE = swallowstalker/kapancuti-base:$(BASE_VERSION)

all: test build push

test:
	python -m unittest tests/*.py

build-base:
	docker build -t $(BASE_IMAGE) -f Dockerfile.base .

push-base:
	echo "$(DOCKER_PASSWORD)" | docker login -u "$(DOCKER_USERNAME)" --password-stdin
	docker push swallowstalker/$(BASE_IMAGE)

build:
	docker build -t $(IMAGE) -f Dockerfile .

push:
	echo "$(DOCKER_PASSWORD)" | docker login -u "$(DOCKER_USERNAME)" --password-stdin
	docker push swallowstalker/$(IMAGE)
