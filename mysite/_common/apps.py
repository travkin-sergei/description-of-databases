# _common/apps.py
"""
Базовые классы AppConfig для всех приложений проекта
"""
from django.apps import AppConfig


class CommonInfraConfig(AppConfig):
    name = '_common'

    def ready(self):
        import _common.schema
