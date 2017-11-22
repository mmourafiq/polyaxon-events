# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import polyaxon_gpustat

from polyaxon_k8s.constants import ContainerStatuses


from polyaxon_events.job_containers import JobContainers

logger = logging.getLogger('polyaxon.resources')


def get_container_resources(container):
    # Check if the container is running
    if container.status != ContainerStatuses.RUNNING:
        logger.info("`{}` container is not running".format(container.name))
        JobContainers.remove_container(container.id)
        return

    job_id = JobContainers.get_job(container.id)
    if not job_id:
        logger.info("`{}` container is not recognised".format(container.name))
        return

    logger.info("Streaming resources for container {} in job `{}` ".format(container.id, job_id))

    stats = container.stats(decode=True, stream=False)
    precpu_stats = stats['precpu_stats']
    cpu_stats = stats['cpu_stats']

    pre_total_usage = float(precpu_stats['cpu_usage']['total_usage'])
    total_usage = float(cpu_stats['cpu_usage']['total_usage'])
    delta_total_usage = total_usage - pre_total_usage

    pre_system_cpu_usage = float(precpu_stats['system_cpu_usage'])
    system_cpu_usage = float(cpu_stats['system_cpu_usage'])
    delta_system_cpu_usage = system_cpu_usage - pre_system_cpu_usage

    percpu_usage = cpu_stats['cpu_usage']['percpu_usage']
    num_cpu_cores = len(percpu_usage)
    cpu_percentage = 0.
    percpu_percentage = [0.] * num_cpu_cores
    if delta_total_usage > 0 and delta_system_cpu_usage > 0:
        cpu_percentage = (delta_total_usage / delta_system_cpu_usage) * num_cpu_cores * 100.0
        percpu_percentage = [cpu_usage / total_usage * cpu_percentage for cpu_usage in percpu_usage]

    memory_used = int(stats['memory_stats']['usage'])
    memory_limit = int(stats['memory_stats']['limit'])

    return {
        'cpu_percentage': cpu_percentage,
        'percpu_percentage': percpu_percentage,
        'memory_used': memory_used,
        'memory_limit': memory_limit
    }


def get_gpu_resources():
    if not polyaxon_gpustat.has_gpu_nvidia:
        return

    return polyaxon_gpustat.query()
