# app_updates/app.py
from django.apps import AppConfig


class MyUpdatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_updates'
