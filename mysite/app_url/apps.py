# app_url/apps.py
from django.apps import AppConfig


class AppLinkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_url'
    db_schema = 'app_url'
    verbose_name = 'Валидация URL'


name = AppLinkConfig.name
db_schema = AppLinkConfig.db_schema
