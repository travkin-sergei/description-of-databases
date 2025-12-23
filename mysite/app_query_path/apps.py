# app_query_path/apps.py
from django.apps import AppConfig


class MyQueryPathConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_query_path'