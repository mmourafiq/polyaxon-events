# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import os
import time

from kubernetes import watch
from kubernetes.client.rest import ApiException

from polyaxon_k8s.manager import K8SManager
from polyaxon_k8s.constants import PodConditions, PodLifeCycle

from polyaxon_events import settings
from polyaxon_events.publisher import Publisher

logger = logging.getLogger('polyaxon.events')


def get_pod_status(event, warnings=None):
    warnings = warnings or []
    # For terminated pods that failed and successfully terminated pods
    if event.status.phase in [PodLifeCycle.FAILED, PodLifeCycle.SUCCEEDED]:
        return event.status.phase

    conditions = {c.type: c.status for c in event.status.conditions}

    if conditions[PodConditions.INITIALIZED] and conditions[PodConditions.READY]:
        return PodLifeCycle.SUCCEEDED

    # If the pod would otherwise be pending but has warning then label it as
    # failed and show and error to the user.
    if len(warnings) > 0:
        return PodLifeCycle.FAILED

    # Unknown?
    return PodLifeCycle.UNKNOWN


def parse_event(raw_event):
    event_type = raw_event['type']
    event = raw_event['object']
    labels = event.metadata.labels
    if labels['types'] != 'experiments':
        return
    pod_phase = event.status.phase
    deletion_timestamp = event.metadata.deletion_timestamp
    pod_conditions = event.status.conditions
    container_statuses = event.status.container_statuses
    container_statuses_by_name = {
        container_status.name: {
            'ready': container_status.ready,
            'state': container_status.state,
        } for container_status in container_statuses
    }

    return {
        'event_type': event_type,
        'labels': labels,
        'pod_phase': pod_phase,
        'pod_status': get_pod_status(event),
        'deletion_timestamp': deletion_timestamp,
        'pod_conditions': pod_conditions,
        'container_statuses': container_statuses_by_name
    }


def run(k8s_manager, publisher):
    w = watch.Watch()

    for event in w.stream(k8s_manager.k8s_api.list_namespaced_pod, label_selectors):
        logger.debug("event: %s" % event)

        parsed_event = parse_event(event)

        if parsed_event:
            publisher.publish(parsed_event)


def main():
    k8s_manager = K8SManager(namespace=settings.NAMESPACE, in_cluster=True)
    publisher = Publisher(os.environ['POLYAXON_JOB_STATUS_ROUTING_KEY'])
    while True:
        try:
            run(k8s_manager, publisher)
        except ApiException as e:
            logger.error(
                "Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
            time.sleep(settings.LOG_SLEEP_INTERVAL)
        except Exception as e:
            logger.exception("Unhandled exception occurred.")


if __name__ == '__main__':
    main()
