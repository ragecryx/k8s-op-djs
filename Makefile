
NODES_NUM ?= 3
K8S_VERSION ?= 1.23.17
MINIKUBE_DRIVER ?= docker

DOCKER_IMAGE_NAME ?= djs-demo
DOCKER_IMAGE_TAG ?= 1.0
DOCKER_IMAGE_TAG_NEXT ?= 1.2


.PHONY: minikube-start
minikube-start:
	minikube start --nodes=$(NODES_NUM) --kubernetes-version=v$(K8S_VERSION) --driver=$(MINIKUBE_DRIVER)

.PHONY: minikube-stop
minikube-stop:
	minikube stop

.PHONY: docker-image
docker-image:
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) -f Dockerfile .

.PHONY: update-image
update-image:
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) -f Dockerfile .
	minikube image load $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)

requirements.txt: requirements.in
	pip-compile --generate-hashes --resolver=backtracking requirements.in

.PHONY: install-deps
install-deps:
	pip install -r requirements.txt

.PHONY: create-demo-objects
create-demo-objects:
	kubectl create -f ./mocker/svc.yaml -f ./example-djs.yaml

.PHONY: delete-demo-objects
delete-demo-objects:
	kubectl delete -f ./example-djs.yaml -f ./mocker/svc.yaml

.PHONY: demo-op-rollout
demo-op-rollout:
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG_NEXT) -f Dockerfile .
	minikube image load $(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG_NEXT)
	kubectl set image deployment/djs-operator djs-operator-container=$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG_NEXT)
	kubectl rollout status -w deployment/djs-operator
	kubectl get pods
