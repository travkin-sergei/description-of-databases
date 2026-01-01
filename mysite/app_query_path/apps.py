# app_query_path/apps.py
from django.apps import AppConfig


class AppQueryPathConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_query_path'
    verbose_name = 'Поиск решений'

    def ready(self):
        """Создаем схему с именем приложения"""
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.name}";')
        except:
            pass


app = AppQueryPathConfig.name
