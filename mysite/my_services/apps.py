import sys
from django.apps import AppConfig


class MyServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_services'

    def ready(self):
        """
        При запуске любой команды manage.py Django сначала инициализирует все приложения, вызывая их методы ready().
        В my_services/apps.py метод ready() содержит вызов start(), который выполняет запрос к модели DimSchedule.
        Однако таблица для этой модели создаётся только при применении миграций, которые выполняются после инициализации приложений.
        Поэтому возникает ошибка UndefinedTable: отношение "my_services.dim_schedule" не существует.
        """
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        from .scheduler import start
        start()