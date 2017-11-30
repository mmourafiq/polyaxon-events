# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import time

import pika
from pika.exceptions import ConnectionClosed, ChannelClosed

from polyaxon_events import settings


class Publisher(object):
    AMQP_URL = settings.AMQP_URL
    EXCHANGE = settings.INTERNAL_EXCHANGE
    EXCHANGE_TYPE = 'topic'

    def __init__(self, routing_key, content_type='application/json', delivery_mode=1):
        self._routing_key = routing_key
        self._connection = None
        self._channel = None
        self._properties = pika.BasicProperties(content_type=content_type,
                                                delivery_mode=delivery_mode)
        self.reset()

    def reset(self):
        if self._connection:
            self._connection.close()
        self._connection = pika.BlockingConnection(pika.URLParameters(self.AMQP_URL))
        try:
            self._channel = self._connection.channel()
            self._channel.exchange_declare(exchange=self.EXCHANGE, exchange_type=self.EXCHANGE_TYPE)
        except ChannelClosed:
            self._channel = self._connection.channel()

    def can_publish(self):
        return self._channel is None or not self._channel.is_open

    def publish(self, message):
        if not self.can_publish():
            self.reset()
        while True:
            try:
                self._channel.basic_publish(exchange=self.EXCHANGE,
                                            routing_key=self._routing_key,
                                            body=message,
                                            properties=self._properties)
                break
            except ConnectionClosed:
                time.sleep(settings.AMQP_RECONNECT_INTERVAL)
                self.reset()
