# k8s-op-djs

### How to run

Ensure you have kubectl and minikube installed. It's configured to run with `docker` driver.

1. `make minikube-start` to create and start the cluster.
2. `kubectl apply -f ./djs/crd.yaml` to register the custom resource.
3. `make docker-image` to build docker image.
4. `minikube image load djs-demo:1.0` to load the docker image from your local docker into minikube.
5. In `mocker` directory run `make service-on-minikube`. This will build & load docker image of mock service and start it in the cluster.
6. `kubectl apply -f ./example-rbac.yaml` so Operator has access to the k8s API.
7. `kubectl create -f ./example-djs.yaml` to create a k8s object of `DynamicJobScheduler` kind.
8. `kubectl get jobs` to observe jobs being created, their naming will be `djs-job-<person name>-<uuidv4>`.
9. Use `kubectl logs -f <the name of the djs-operator pod>` to observe what the Operator is processing.

To run step 5 you need to have a Python VirtualEnv created and packages installed with `pip install -r requirements.txt`.
