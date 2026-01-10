from django.apps import AppConfig


class AppDocConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_doc'
    db_schema = 'app_doc'
    verbose_name = 'Список документов'



name = AppDocConfig.name
db_schema = AppDocConfig.db_schema