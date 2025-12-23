# app_request/apps.py
from django.apps import AppConfig


class MyRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_request'
