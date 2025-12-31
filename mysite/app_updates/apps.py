# app_updates/app.py
from django.apps import AppConfig


class AppUpdatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_updates'

    def ready(self):
        """Создаем схему с именем приложения"""
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.name}";')
        except:
            pass


app = AppUpdatesConfig.name
