# apps.py
from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_save, post_delete
import threading
import time
import sys


class MyRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_request'

    def ready(self):
        # Регистрируем сигналы
        self.register_signals()

        # Запускаем планировщик только в основном процессе runserver
        if 'runserver' in sys.argv:
            self.start_scheduler()

    def register_signals(self):
        """Регистрация сигналов"""
        from django.core.management import call_command

        def update_crontab(sender, **kwargs):
            """
            После изменения расписания перегенерируем cron-задачи.
            """
            # Проверяем, что это наша модель
            if sender.__name__ == 'FZSchedule':
                print("Обнаружено изменение FZSchedule, обновляем crontab...")
                try:
                    # Очистить старые задачи
                    call_command('crontab', 'remove')
                    # Добавить новые
                    call_command('crontab', 'add')
                except Exception as e:
                    print(f"Ошибка при обновлении crontab: {e}")

        # Импортируем модель после регистрации функции
        from .models import FZSchedule
        post_save.connect(update_crontab, sender=FZSchedule)
        post_delete.connect(update_crontab, sender=FZSchedule)

    def start_scheduler(self):
        def run():
            # Даем время на полную загрузку приложения
            time.sleep(10)
            while True:
                try:
                    from .models import FZSchedule
                    # Проверяем каждые 5 минут
                    time.sleep(1 * 60)
                    call_command('run_scheduled_checks')
                except Exception as e:
                    print(f"Ошибка в планировщике: {e}")
                    time.sleep(60)  # Ждем минуту перед повторной попыткой

        scheduler_thread = threading.Thread(target=run, daemon=True)
        scheduler_thread.start()
