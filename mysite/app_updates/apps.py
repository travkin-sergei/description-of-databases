# app_updates/app.py
from django.apps import AppConfig


class AppUpdatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_updates'
    db_schema = 'app_updates'
    verbose_name = 'Обновления баз данных.'


name = AppUpdatesConfig.name
db_schema = AppUpdatesConfig.db_schema
