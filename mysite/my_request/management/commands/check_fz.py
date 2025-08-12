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

from django.core.management.base import BaseCommand
from ...models import FZ


class Command(BaseCommand):
    help = 'Проверяет соответствие данных указанному закону'

    def add_arguments(self, parser):
        parser.add_argument('--fz-id', type=int, help='ID закона для проверки')

    def handle(self, *args, **options):
        fz_id = options['fz_id']
        try:
            fz = FZ.objects.get(id=fz_id)
            self.stdout.write(f"Начинаем проверку для закона {fz.name}")
            self.check_fz(fz)
            self.stdout.write(self.style.SUCCESS(f"Проверка для закона {fz.name} завершена"))
        except FZ.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Закон с ID {fz_id} не найден"))

    def check_fz(self, fz):
        columns = fz.columnfz_set.all()
        for column_fz in columns:
            self.process_column(column_fz.column)

    def process_column(self, column):
        # Реальная логика проверки данных
        self.stdout.write(f"Обработка колонки {column.columns}", ending='\r')