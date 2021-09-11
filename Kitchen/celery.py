from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kitchen.settings.__init__')

celery_instance = Celery('Kitchen')

celery_instance.config_from_object('django.conf:__init__', namespace='CELERY')
celery_instance.autodiscover_tasks()


@celery_instance.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
