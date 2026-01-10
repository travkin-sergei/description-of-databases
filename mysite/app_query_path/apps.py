# app_query_path/apps.py
from django.apps import AppConfig


class AppQueryPathConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_query_path'
    db_schema = 'app_query_path'
    verbose_name = 'Поиск решений'


name = AppQueryPathConfig.name
db_schema = AppQueryPathConfig.db_schema