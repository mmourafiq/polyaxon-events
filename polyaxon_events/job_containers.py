# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import redis


class JobContainers(object):
    """Tracks containers currently running and to be monitored."""

    REDIS_CONTAINERS_KEY = 'CONTAINERS'  # Redis set: container ids
    REDIS_CONTAINERS_TO_JOBS = 'CONTAINERS_TO_JOBS'  # Redis hash, maps container id to jobs
    REDIS_POOL = os.environ['POLYAXON_JOB_CONTAINERS_URL']  # Redis pool

    @classmethod
    def _get_redis(cls):
        return redis.Redis(connection_pool=cls.REDIS_POOL)

    @classmethod
    def get_containers(cls):
        red = cls._get_redis()
        red.smembers(cls.REDIS_CONTAINERS_KEY)

    @classmethod
    def get_job(cls, object_id):
        red = cls._get_redis()
        if red.sismember(cls.REDIS_CONTAINERS_KEY, object_id):
            return red.hget(cls.REDIS_CONTAINERS_TO_JOBS, object_id)

    @classmethod
    def monitor(cls, object_id, job_id):
        red = cls._get_redis()
        red.sadd(cls.REDIS_CONTAINERS_KEY, object_id)
        red.hset(cls.REDIS_CONTAINERS_TO_JOBS, object_id, job_id)

    @classmethod
    def remove_container(cls, object_id):
        red = cls._get_redis()
        red.srem(cls.REDIS_CONTAINERS_KEY, object_id)
        red.hdel(cls.REDIS_CONTAINERS_TO_JOBS, object_id)
