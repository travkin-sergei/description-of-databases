# my_services/apps.py
from django.apps import AppConfig


class MyServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_services'

    def ready(self):
        from .scheduler import start
        start()  # При первом старте отключить
        # pass  # При первом старте включить
