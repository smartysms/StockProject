from __future__ import absolute_import, unicode_literals
from kombu import Queue
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockProject.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
app = Celery('StockProject')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# class MyQueue(Queue):
#     def __init__(self, name='', exchange=None, routing_key='',
#                  channel=None, bindings=None, on_declared=None,
#                  **kwargs):
#         super(MyQueue, self).__init__(**kwargs)


# default_queue = MyQueue('celery', exchange='celery', routing_key='celery')
# ask_queue = MyQueue('ask', exchange='ask', routing_key='ask')
# bid_queue = MyQueue('bid', exchange='bid', routing_key='bid')

# app.conf.task_default_name = 'celery'
# app.conf.task_default_exchange = 'celery'
# app.conf.task_default_routing_key = 'celery'

# app.conf.task_queues = (default_queue, ask_queue, bid_queue)
#app.conf.enable_utc = False

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
