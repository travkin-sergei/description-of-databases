# app_services/apps.py
from django.apps import AppConfig
from django.core.signals import request_started


class AppServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_services'
    db_schema = 'app_services'
    verbose_name = 'Информация по сервисам'


name = AppServicesConfig.name
db_schema = AppServicesConfig.db_schema
