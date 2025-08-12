import time
import threading

from django.apps import AppConfig
from django.core.management import call_command


class MyRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_request'

    def ready(self):
        # Запускаем периодическую проверку только в основном процессе
        # (не в reload-процессе разработческого сервера)
        import sys
        if 'runserver' in sys.argv:
            self.start_scheduler()

    def start_scheduler(self):
        def run():
            while True:
                try:
                    from .models import FZSchedule
                    # Проверяем каждые 5 минут
                    time.sleep(5 * 60)
                    call_command('run_scheduled_checks')
                except Exception as e:
                    print(f"Ошибка в планировщике: {e}")

        scheduler_thread = threading.Thread(target=run, daemon=True)
        scheduler_thread.start()
