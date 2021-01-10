from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

BROKER_REDIS_PORT = 6379
BROKER_REDIS_DB = 0
BROKER_REDIS_HOST = os.environ.get(
    'REDIS_BROKER', 'redis_broker')

BROKER_URL = 'redis://{host}:{port}/{db}'.format(
    host=BROKER_REDIS_HOST,
    port=BROKER_REDIS_PORT,
    db=BROKER_REDIS_DB
)

# configure queues, currently we have only one
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)


CELERY_IMPORTS = [
    'utils',
]

celery_app = Celery('stonks',
                    broker=BROKER_URL, include=CELERY_IMPORTS)


# Celery configuration
# http://docs.celeryproject.org/en/latest/userguide/configuration.html
celery_app.broker_connection_timeout = 10
celery_app.task_acks_late = True
celery_app.task_ignore_result = True
celery_app.task_reject_on_worker_lost = True
# in seconds
celery_app.result_expires = 600
celery_app.worker_hijack_root_logger = False
celery_app.worker_max_tasks_per_child = 1000

celery_app.conf.beat_schedule = {
    'update-stonks': {
        'task': 'utils.update_stonks',
        'schedule': crontab(hour=0, minute=0),
    }
}