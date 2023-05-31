import os
from datetime import datetime, UTC, timedelta as td
import requests
from environs import Env
import kopf
from kubernetes import client, config

env = Env()
env.read_env()

JOB_DISPATCH_TIMEFRAME_MIN = env.int("JOB_DISPATCH_TIMEFRAME_MIN", 30)
TIMER_IDLING_SEC = env.int("TIMER_IDLING_SEC", 15)
TIMER_INTERVAL_SEC = env.int("TIMER_INTERVAL_SEC", 60)
JOB_DISPATCH_ACTIVE = True
JOBS_ALREADY_DISPATCHED = set()

if "KUBERNETES_SERVICE_HOST" in os.environ:
    config.load_incluster_config()
else:
    config.load_kube_config()

k8s_core = client.CoreV1Api()
k8s_batch = client.BatchV1Api()


def tz_aware_utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def add_running_to_already_dispatched(namespace: str):
    jobs_result = k8s_batch.list_namespaced_job(namespace)
    for job in jobs_result.items:
        JOBS_ALREADY_DISPATCHED.add(job.metadata.name)


@kopf.on.resume('koutsikos.dev', 'v1', 'dynamicjobschedulers',)
@kopf.on.create('koutsikos.dev', 'v1', 'dynamicjobschedulers',)
def on_init(spec, **_):
    job_namespace = spec.get('job_namespace')
    add_running_to_already_dispatched(job_namespace)


@kopf.on.cleanup()
async def on_cleanup(logger, **kwargs):
    # Called on termination
    global JOB_DISPATCH_ACTIVE
    JOB_DISPATCH_ACTIVE = False


@kopf.timer(
    'koutsikos.dev', 'v1', 'dynamicjobschedulers',
    interval=TIMER_INTERVAL_SEC, idle=TIMER_IDLING_SEC
)
def scheduler_tick(spec, **kwargs):
    api_endpoint = spec.get('api_endpoint')
    job_namespace = spec.get('job_namespace')
    job_image = spec.get('job_image')

    response = requests.get(api_endpoint)
    data = response.json()

    now = tz_aware_utc_now()
    now_ts = int(now.timestamp())
    max_ts = int((now + td(minutes=JOB_DISPATCH_TIMEFRAME_MIN)).timestamp())

    for entry in data:
        job_name = f"djs-job-{entry['name']}-{entry['id']}"

        if not (now_ts < entry["start_time"] <= max_ts):
            continue

        # If the job is already running don't try to add again
        if job_name in JOBS_ALREADY_DISPATCHED:
            continue

        print(f"Launching job: {job_name} with image {job_image}")
        ttl = int(td(minutes=5).total_seconds())

        common_labels = {
            "person": entry['name']
        }

        job = client.V1Job()
        job.api_version = 'batch/v1'
        job.kind = 'Job'
        job.metadata = client.V1ObjectMeta(
            name=job_name,
            labels={
                "app": "djs-job",
            } | common_labels
        )
        job.spec = client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        "app": "djs-job-pod",
                    } | common_labels
                ),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name=f"djs-job-pod-container",
                        image=job_image,
                        # image_pull_policy='Always',
                    )],
                    restart_policy='Never',
                )
            ),
            ttl_seconds_after_finished=ttl
        )

        global JOB_DISPATCH_ACTIVE
        if JOB_DISPATCH_ACTIVE:
            k8s_batch.create_namespaced_job(
                job_namespace,
                job
            )
            JOBS_ALREADY_DISPATCHED.add(job_name)
