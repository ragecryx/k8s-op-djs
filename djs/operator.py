from datetime import datetime, UTC, timedelta as td
from hashlib import md5

import kopf
import requests
import time

from kubernetes import client, config

config.load_kube_config()
k8s_core = client.CoreV1Api()
k8s_batch = client.BatchV1Api()

md5hex = lambda x: md5(x.encode('utf-8')).hexdigest()


def tz_aware_utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


@kopf.daemon('koutsikos.dev', 'v1', 'dynamicjobschedulers')
def process_daemon(spec, stopped, **kwargs):
    job_namespace = spec.get('job_namespace')
    api_endpoint = spec.get('api_endpoint')
    polling_interval = spec.get('poll_interval')
    image_name = spec.get('image_name')
    image_tag = spec.get('image_tag')

    while not stopped:
        response = requests.get(api_endpoint)
        data = response.json()

        for entry in data:
            id: str = entry.get('name')
            job_name = f"djs-job-{md5hex(id)}"
            print(f"Launching job for '{id}' with name: {job_name}")
            ttl = int(td(hours=24).total_seconds())

            job = client.V1Job()
            job.api_version = 'batch/v1'
            job.kind = 'Job'
            job.metadata = client.V1ObjectMeta(name=job_name)
            job.spec = client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name='job-container',
                            image=f"{image_name}:{image_tag}",
                        )],
                        restart_policy='Never'
                    )
                ),
                ttl_seconds_after_finished=ttl
            )

            k8s_batch.create_namespaced_job(
                job_namespace,
                job
            )
        time.sleep(polling_interval)
