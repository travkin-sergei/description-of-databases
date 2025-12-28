# app_auth/apps.py
from django.apps import AppConfig
from django.contrib.auth import user_logged_in

class AppAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_auth'
    verbose_name = 'Авторизация и профили'

    def ready(self):
        from .signals import update_login_stats
        user_logged_in.connect(update_login_stats)