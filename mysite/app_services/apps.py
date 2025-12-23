# app_services/apps.py
from django.apps import AppConfig
from django.core.signals import request_started


class MyServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_services'

    def ready(self):
        # Подключаем обработчик к сигналу первого запроса
        request_started.connect(self.on_first_request)

    def on_first_request(self, **kwargs):
        """
        Выполняется при первом HTTP‑запросе к серверу.
        К этому моменту Django гарантированно готов.
        """
        # Импортируем и запускаем scheduler
        from .scheduler import start
        start()

        # Отключаем сигнал, чтобы не срабатывал на каждый запрос
        request_started.disconnect(self.on_first_request)
