from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    name = 'application'

    def ready(self):
        from . import aync_task_my
        aync_task_my.start()