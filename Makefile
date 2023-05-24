
NODES_NUM ?= 3
K8S_VERSION ?= 1.23.17
MINIKUBE_DRIVER ?= docker

DOCKER_IMAGE_NAME ?= djs-demo
DOCKER_IMAGE_TAG ?= 1.0


.PHONY: minikube-start
minikube-start:
	minikube start --nodes=$(NODES_NUM) --kubernetes-version=v$(K8S_VERSION) --driver=$(MINIKUBE_DRIVER)

.PHONY: minikube-stop
minikube-stop:
	minikube stop

.PHONY: docker-image
docker-image:
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) -f Dockerfile .

requirements.txt: requirements.in
	pip-compile --generate-hashes --resolver=backtracking requirements.in

.PHONY: install-deps
install-deps:
	pip install -r requirements.txt
