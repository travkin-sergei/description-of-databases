# _common/schema_init.py
from django.apps import apps
from django.db import connection
from django.db.models.signals import pre_migrate

def create_schemas(sender, using, **kwargs):
    with connection.cursor() as cursor:
        for app in apps.get_app_configs():
            schema = getattr(app, 'db_schema', None)
            if schema:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')

# защита от повторного подключения
if not getattr(pre_migrate, '_schemas_connected', False):
    pre_migrate.connect(create_schemas)
    pre_migrate._schemas_connected = True
