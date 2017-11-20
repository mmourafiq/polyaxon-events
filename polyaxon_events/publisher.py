# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import time

import pika
from pika.exceptions import ConnectionClosed

import settings
from logger import logger


class EventPublisher(object):
    AMQP_URL = settings.AMQP_URL
    LOG_ROUTING_KEY = settings.LOG_ROUTING_KEY
    EXCHANGE = settings.INTERNAL_EXCHANGE
    EXCHANGE_TYPE = 'topic'

    def __init__(self):
        self._connection = None
        self._channel = None
        self._properties = pika.BasicProperties(content_type='application/json', delivery_mode=1)
        self.reset()

    def reset(self):
        if self._connection:
            self._connection.close()
        self._connection = pika.BlockingConnection(pika.URLParameters(self.AMQP_URL))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self.EXCHANGE,
                                       exchange_type=self.EXCHANGE_TYPE)

    def can_publish(self):
        return self._channel is None or not self._channel.is_open

    def publish(self, message):
        if not self.can_publish():
            self.reset()
        while True:
            try:
                self._channel.basic_publish(exchange=self.EXCHANGE,
                                            routing_key=self.LOG_ROUTING_KEY,
                                            body=message,
                                            properties=self._properties)
                logger.debug('published: {}'.format(message[:100]))
                break
            except ConnectionClosed:
                time.sleep(1)
                self.reset()
