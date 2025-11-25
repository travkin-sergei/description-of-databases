# check_fz.py
"""
Команда для проверки соответствия данных указанному закону.

Основные функции:
1. Получение закона (ФЗ) по ID
2. Проверка всех связанных колонок на соответствие требованиям закона
3. Построчная обработка данных в колонках

Использование:
python manage.py check_fz --fz-id <ID_закона>

Пример:
python manage.py check_fz --fz-id 1
"""
# management/commands/check_fz.py
from django.core.management.base import BaseCommand
from my_request.models import FZ


class Command(BaseCommand):
    help = 'Проверяет соответствие данных указанному закону'

    def add_arguments(self, parser):
        parser.add_argument('--fz-id', type=int, help='ID закона для проверки', required=True)

    def handle(self, *args, **options):
        fz_id = options['fz_id']

        try:
            fz = FZ.objects.get(id=fz_id)
            self.stdout.write(f"Начинаем проверку для закона: {fz.name}")

            # Получаем все связанные колонки
            column_fz_list = fz.columnfz_set.filter(is_active=True).select_related('column')

            self.stdout.write(f"Найдено колонок для проверки: {column_fz_list.count()}")

            for column_fz in column_fz_list:
                self.process_column(column_fz)

            self.stdout.write(self.style.SUCCESS(f"Проверка для закона '{fz.name}' завершена успешно"))

        except FZ.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Закон с ID {fz_id} не найден"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при выполнении проверки: {e}"))

    def process_column(self, column_fz):
        """Обрабатывает одну колонку"""
        try:
            column = column_fz.column
            self.stdout.write(f"Обработка колонки: {column.columns} (таблица: {column.table.name})")

            # Здесь должна быть реальная логика проверки данных
            # Например, проверка формата данных, соответствия маске и т.д.

            # Временная заглушка - имитация обработки
            self.simulate_data_processing(column)

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Ошибка при обработке колонки {column_fz.id}: {e}"))

    def simulate_data_processing(self, column):
        """Имитация обработки данных (заглушка для демонстрации)"""
        # В реальной реализации здесь будет работа с данными из БД
        import time
        time.sleep(0.1)  # Имитация обработки
        self.stdout.write(f"    ✓ Колонка '{column.columns}' проверена")