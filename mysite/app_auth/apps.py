# app_auth/apps.py
from django.apps import AppConfig

class AppAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_auth'
    verbose_name = 'Авторизация и профили'

    def ready(self):
        pass