# run_scheduled_checks.py
"""
Команда для выполнения проверок соответствия данных законодательным требованиям по расписанию.

Основные функции:
1. Автоматический поиск запланированных проверок, готовых к выполнению
2. Последовательный запуск проверок для каждого активного расписания
3. Обновление статусов последнего и следующего выполнения

Логика работы:
- Проверяет расписания (FZSchedule), у которых next_run наступил (с 5-минутным буфером)
- Для каждого найденного расписания выполняет проверку соответствия
- После выполнения обновляет last_run и вычисляет next_run

Использование:
python manage.py run_scheduled_checks

Рекомендуется настраивать вызов через системный cron каждые 5-10 минут:
*/5 * * * * /path/to/python manage.py run_scheduled_checks >> /var/log/fz_checks.log
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ...models import FZSchedule


class Command(BaseCommand):
    help = 'Запускает проверки по расписанию'

    def handle(self, *args, **options):
        now = timezone.now()
        # Берем задачи, у которых next_run в прошлом (пора запускать)
        # И добавляем небольшой буфер (5 минут), чтобы компенсировать возможные задержки
        schedules = FZSchedule.objects.filter(
            next_run__lte=now + timedelta(minutes=5),
            is_active=True
        )

        for schedule in schedules:
            self.stdout.write(f"Запуск проверки для {schedule.fz.name} по расписанию {schedule.cron}")
            self.run_fz_check(schedule)
            schedule.last_run = now
            schedule.update_next_run()
            schedule.save()

    def run_fz_check(self, schedule):
        # Здесь реализация проверки конкретного закона
        # Можно вызывать другую команду или напрямую импортировать нужные функции
        try:
            # Примерная реализация проверки
            columns_count = schedule.fz.columnfz_set.count()
            self.stdout.write(f"Проверяем {columns_count} колонок для закона {schedule.fz.name}")
            # ... логика проверки ...
            self.stdout.write(self.style.SUCCESS(f"Проверка для {schedule.fz.name} завершена"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при проверке {schedule.fz.name}: {e}"))