# _common/apps.py
"""
Базовые классы AppConfig для всех приложений проекта
"""
from django.apps import AppConfig

class CommonInfraConfig(AppConfig):
    name = '_common'

    def ready(self):
        # подключаем schema_init один раз
        import _common.schema_init
