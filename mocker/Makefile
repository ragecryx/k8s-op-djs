
DOCKER_IMAGE_NAME ?= djs-mocker
DOCKER_IMAGE_TAG ?= 1.0


.PHONY: docker-image
docker-image:
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) -f Dockerfile .

requirements.txt: requirements.in
	pip-compile --generate-hashes --resolver=backtracking requirements.in

.PHONY: install-deps
install-deps:
	pip install -r requirements.txt

.PHONY: service-on-minikube
service-on-minikube:
	pip install -r requirements.txt
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) -f Dockerfile .
	minikube image load $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)
	kubectl create -f ./svc.yaml

.PHONY: remove-service
remove-service:
	kubectl delete -f ./svc.yaml
