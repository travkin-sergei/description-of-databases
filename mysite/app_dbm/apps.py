# app_dbm/apps.py
from django.apps import AppConfig


class AppDbmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dbm'
    db_schema = 'app_dbm'
    verbose_name = 'Описание баз данных'


name = AppDbmConfig.name
db_schema = AppDbmConfig.db_schema
