# app_dict/apps.py
from django.apps import AppConfig


class AppDictConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dict'
    db_schema = 'app_dict'
    verbose_name = 'Термины и определения'


name = AppDictConfig.name
db_schema = AppDictConfig.db_schema
