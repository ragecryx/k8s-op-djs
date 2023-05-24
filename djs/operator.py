import os
from datetime import datetime, UTC, timedelta as td
from hashlib import md5

import kopf
import requests
import time

from kubernetes import client, config

if "KUBERNETES_SERVICE_HOST" in os.environ:
    config.load_incluster_config()
else:
    config.load_kube_config()

k8s_core = client.CoreV1Api()
k8s_batch = client.BatchV1Api()


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
        now = tz_aware_utc_now()
        now_ts = int(now.timestamp())
        max_ts = int((now + td(minutes=30)).timestamp())

        for entry in data:
            job_name = f"djs-job-{entry['name']}-{entry['id']}"

            if not (now_ts < entry["start_time"] <= max_ts):
                continue

            # If the job is already running don't try to add again
            jobs_result = k8s_batch.list_namespaced_job(job_namespace)
            matching_jobs = [
                job for job in jobs_result.items
                if job.metadata.name == job_name
            ]
            if matching_jobs:
                continue

            print(f"Launching job: {job_name}")
            ttl = int(td(minutes=5).total_seconds())

            job = client.V1Job()
            job.api_version = 'batch/v1'
            job.kind = 'Job'
            job.metadata = client.V1ObjectMeta(name=job_name)
            job.spec = client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={
                            "app": "djs-job",
                            "person": entry['name']
                        }
                    ),
                    spec=client.V1PodSpec(
                        containers=[client.V1Container(
                            name='job-container',
                            # image_pull_policy='Always',
                            image=f"{image_name}:{image_tag}",
                        )],
                        restart_policy='Never',
                    )
                ),
                ttl_seconds_after_finished=ttl
            )

            k8s_batch.create_namespaced_job(
                job_namespace,
                job
            )
        time.sleep(polling_interval)
