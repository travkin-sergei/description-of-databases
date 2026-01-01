# app_services/apps.py
from django.apps import AppConfig
from django.core.signals import request_started


class AppServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_services'
    verbose_name = 'Информация по сервисам'


    def ready(self):
        """Создаем схему с именем приложения"""
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.name}";')
        except:
            pass



app = AppServicesConfig.name
