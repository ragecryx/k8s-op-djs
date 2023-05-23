# k8s-op-djs

### How to run

Ensure you have kubectl and minikube installed. It's configured to run with `docker` driver.

1. `make minikube-start` to create and start the cluster.
2. `kubectl apply -f ./djs/crd.yaml` to register the custom resource.
3. `make docker-image` to build docker image.
4. `minikube image load djs-demo:1.0` to load the docker image from your local docker into minikube.
5. In a separate terminal `python3 -m kopf run ./djs/operator.py` to start the operator locally.
6. `kubectl create -f ./test-djs.yaml` to create a k8s object of `DynamicJobScheduler` kind.
7. `kubectl get jobs` to observe jobs being created, their naming will be `djs-job-<some md5 checksum>`.

To run step 5 you need to have a Python VirtualEnv created and packages installed with `pip install -r requirements.txt`.
