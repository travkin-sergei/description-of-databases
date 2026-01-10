# app_request/apps.py
from django.apps import AppConfig


class AppRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_request'
    db_schema = 'app_request'
    verbose_name = 'Запросы по категориям'



name = AppRequestConfig.name
db_schema = AppRequestConfig.db_schema