# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import os

import sys


NAMESPACE = os.environ['POLYAXON_K8S_NAMESPACE']
AMQP_URL = os.environ['POLYAXON_AMQP_URL']
AMQP_RECONNECT_INTERVAL = int(os.environ.get('POLYAXON_AMQP_RECONNECT_INTERVAL', 1))
INTERNAL_EXCHANGE = os.environ['POLYAXON_INTERNAL_EXCHANGE']
LOG_SLEEP_INTERVAL = int(os.environ.get('POLYAXON_LOG_SLEEP_INTERVAL', 1))
DEBUG = os.environ.get('POLYAXON_DEBUG')

# mapping from k8s event types to event levels
LEVEL_MAPPING = {
    'normal': 'info',
}

log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s',
                    level=log_level,
                    stream=sys.stdout)
