# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os

from logger import configure_logger

NAMESPACE = os.environ.get('POLYAXON_K8S_NAMESPACE')
AMQP_URL = os.environ.get('POLYAXON_AMQP_URL')
LOG_ROUTING_KEY = os.environ.get('POLYAXON_LOG_ROUTING_KEY')
INTERNAL_EXCHANGE = os.environ.get('POLYAXON_INTERNAL_EXCHANGE')
LOG_SLEEP_INTERVAL = os.environ.get('POLYAXON_LOG_SLEEP_INTERVAL', 5)
DEBUG = os.environ.get('POLYAXON_DEBUG')

# mapping from k8s event types to event levels
LEVEL_MAPPING = {
    'normal': 'info',
}

configure_logger(DEBUG)
