# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import os
import time

from polyaxon_k8s.constants import PodLifeCycle
from polyaxon_k8s.manager import K8SManager

from polyaxon_events import settings
from polyaxon_events.publisher import Publisher

logger = logging.getLogger('polyaxon.sidecar')


def run(k8s_manager, publisher, pod_id, job_id):
    raw = k8s_manager.k8s_api.read_namespaced_pod_log(pod_id,
                                                      k8s_manager.namespace,
                                                      container=job_id,
                                                      follow=True,
                                                      _preload_content=False)
    for line in raw.stream():
        logger.info("Publishing event: {}".format(line))
        publisher.publish(line)


def can_log(k8s_manager, pod_id):
    status = k8s_manager.k8s_api.read_namespaced_pod_status(pod_id,
                                                            k8s_manager.namespace)
    logger.debug(status)
    while status.status.phase != PodLifeCycle.RUNNING:
        time.sleep(settings.LOG_SLEEP_INTERVAL)
        status = k8s_manager.k8s_api.read_namespaced_pod_status(pod_id,
                                                                k8s_manager.namespace)


def main():
    pod_id = os.environ['POLYAXON_POD_ID']
    job_id = os.environ['POLYAXON_JOB_ID']
    k8s_manager = K8SManager(namespace=settings.NAMESPACE, in_cluster=True)
    can_log(k8s_manager, pod_id)
    # TODO: add experiment id and job id to the routing key
    publisher = Publisher(os.environ['POLYAXON_ROUTING_KEYS_LOGS_SIDECARS'],
                          content_type='text/plain')
    run(k8s_manager, publisher, pod_id, job_id)
    logger.debug('Finished logging')


if __name__ == '__main__':
    main()
