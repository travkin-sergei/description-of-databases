# app_dbm/apps.py
from django.apps import AppConfig


class MyDbmatchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dbm'
