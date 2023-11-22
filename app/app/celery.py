from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
# from celery.signals import setup_logging  # noqa

# Set the default Django settings module for the 'celery' program.
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.development')

celery_app = Celery('app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
#
# @setup_logging.connect
# def config_loggers(*args, **kwargs):
#     from logging.config import dictConfig  # noqa
#     from django.conf import settings  # noqa
#
#     dictConfig(settings.LOGGING)

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()


@celery_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
