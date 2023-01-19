# MLRun Community Edition: MLRun Open Source Stack for MLOps

This Helm charts bundles open source software stack for advanced ML operations

## Chart Details

The Open source MLRun ce chart includes the following stack:

* Nuclio - https://github.com/nuclio/nuclio
* MLRun - https://github.com/mlrun/mlrun
* Jupyter - https://github.com/jupyter/notebook (+MLRun integrated)
* MPI Operator - https://github.com/kubeflow/mpi-operator
* Minio - https://github.com/minio/minio/tree/master/helm/minio
* Spark Operator - https://github.com/GoogleCloudPlatform/spark-on-k8s-operator
* Pipelines - https://github.com/kubeflow/pipelines
* Prometheus stack - https://github.com/prometheus-community/helm-charts

## Prerequisites

- docker desktop with enabled kubernetes

- registered docker hub

- Helm >=3.6 installed from [here](https://helm.sh/docs/intro/install/)

- Preprovisioned Kubernetes StorageClass
  
> In case your Kubernetes flavor is not shipped with a default StorageClass, you may use [local-path by Rancher](https://github.com/rancher/local-path-provisioner)
> 1. Install it via [this link](https://github.com/rancher/local-path-provisioner#installation)  
> 2. Set as default by executing `kubectl patch storageclass local-path -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'`


## Installing the Chart

Create a namespace for the deployed components:
```bash
kubectl create namespace mlrun
```

Add the mlrun ce helm chart repo
```bash
helm repo add mlrun https://mlrun.github.io/ce
```

To work with the open source MLRun stack, you must an accessible docker-registry. The registry's URL and credentials
are consumed by the applications via a pre-created secret

To create a secret with your docker-registry details:

```bash
kubectl --namespace mlrun create secret docker-registry registry-credentials \
    --docker-username <registry-username> \
    --docker-password <login-password> \
    --docker-server https://index.docker.io/v1/ \
    --docker-email <user-email>
```

To install the chart with the release name `my-mlrun` use the following command, 
note the reference to the pre-created `registry-credentials` secret in `global.registry.secretName`, 
and a `global.registry.url` with an appropriate registry URL which can be authenticated by this secret:

```bash
helm --namespace mlrun \
    install my-mlrun \
    --wait \
    --set global.registry.url=index.docker.io/iguazio \
    --set global.registry.secretName=registry-credentials \
    mlrun/mlrun-ce
```
