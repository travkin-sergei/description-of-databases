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
# management/commands/run_scheduled_checks.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from my_request.models import FZSchedule


class Command(BaseCommand):
    help = 'Запускает проверки по расписанию'

    def handle(self, *args, **options):
        now = timezone.now()

        self.stdout.write(f"Поиск запланированных проверок на {now}")

        # Ищем расписания, которые нужно выполнить
        schedules = FZSchedule.objects.filter(
            next_run__lte=now + timedelta(minutes=5),  # Буфер 5 минут
            is_active=True
        ).select_related('fz')

        self.stdout.write(f"Найдено расписаний для выполнения: {schedules.count()}")

        if not schedules.exists():
            self.stdout.write("Нет активных расписаний для выполнения")
            return

        for schedule in schedules:
            self.stdout.write(f"\n--- Запуск проверки: {schedule.name} ---")
            self.run_scheduled_check(schedule, now)

        self.stdout.write(self.style.SUCCESS("\nВсе запланированные проверки завершены"))

    def run_scheduled_check(self, schedule, current_time):
        """Выполняет проверку по расписанию"""
        try:
            # Обновляем время последнего запуска
            schedule.last_run = current_time
            schedule.update_next_run()

            # Вызываем команду проверки ФЗ
            self.stdout.write(f"Запуск проверки ФЗ: {schedule.fz.name} (ID: {schedule.fz.id})")

            call_command('check_fz', fz_id=schedule.fz.id)

            # Сохраняем обновленное расписание
            schedule.save()

            self.stdout.write(self.style.SUCCESS(f"Проверка '{schedule.name}' завершена успешно"))
            self.stdout.write(f"Следующий запуск: {schedule.next_run}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при выполнении проверки '{schedule.name}': {e}"))
            # Даже при ошибке обновляем next_run, чтобы не зацикливаться на ошибке
            try:
                schedule.last_run = current_time
                schedule.update_next_run()
                schedule.save()
            except Exception as save_error:
                self.stdout.write(self.style.ERROR(f"Ошибка при сохранении расписания: {save_error}"))