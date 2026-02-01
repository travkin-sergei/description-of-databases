# _common/cron_processing.py
import re
from datetime import datetime, timedelta
from typing import Set, Optional


class UniversalCronParser:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_parser()
        return cls._instance

    def _init_parser(self):
        """Инициализация парсера (выполняется один раз)"""
        self.month_names = {
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
        }
        self.day_names = {
            'SUN': 0, 'MON': 1, 'TUE': 2, 'WED': 3,
            'THU': 4, 'FRI': 5, 'SAT': 6
        }

    def get_next_execution(self, cron_expr: str, from_date: Optional[datetime] = None) -> datetime:
        """
        Универсальный метод для получения следующего выполнения cron.
        """
        if from_date is None:
            from_date = datetime.now()

        # Нормализуем выражение до 7 полей
        fields = self._normalize_cron(cron_expr)

        # Парсим все поля
        second_set = self._parse_field(fields[0], 0, 59, is_second=True)
        minute_set = self._parse_field(fields[1], 0, 59)
        hour_set = self._parse_field(fields[2], 0, 23)
        day_month_set = self._parse_field(fields[3], 1, 31)
        month_set = self._parse_field(fields[4], 1, 12)
        day_week_set = self._parse_field(fields[5], 0, 6)
        year_set = self._parse_field(fields[6], from_date.year, from_date.year + 10)

        # Ищем следующее выполнение
        current = from_date + timedelta(seconds=1)

        for _ in range(60 * 60 * 24 * 365 * 5):  # 5 лет в секундах
            # Проверка года
            if current.year not in year_set:
                current = datetime(current.year + 1, 1, 1, 0, 0, 0)
                continue

            # Проверка месяца
            if current.month not in month_set:
                next_month = current.month + 1 if current.month < 12 else 1
                next_year = current.year if current.month < 12 else current.year + 1
                current = datetime(next_year, next_month, 1, 0, 0, 0)
                continue

            # Проверка дня (месяца и недели)
            day_month_valid = current.day in day_month_set
            day_week_valid = (current.weekday() + 1) % 7 in day_week_set

            # Обработка wildcards
            day_month_wild = fields[3] in ('*', '?', '')
            day_week_wild = fields[5] in ('*', '?', '')

            if day_month_wild and day_week_wild:
                day_valid = day_month_valid or day_week_valid
            elif day_month_wild:
                day_valid = day_week_valid
            elif day_week_wild:
                day_valid = day_month_valid
            else:
                day_valid = day_month_valid and day_week_valid

            if not day_valid:
                current = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                continue

            # Проверка часа
            if current.hour not in hour_set:
                current = (current + timedelta(hours=1)).replace(minute=0, second=0)
                continue

            # Проверка минут
            if current.minute not in minute_set:
                current = (current + timedelta(minutes=1)).replace(second=0)
                continue

            # Проверка секунд
            if current.second not in second_set:
                current += timedelta(seconds=1)
                continue

            # Все условия выполнены
            return current

        raise ValueError(f"Не удалось найти выполнение для: {cron_expr}")

    def _normalize_cron(self, cron_expr: str) -> list:
        """Нормализует cron выражение до 7 полей"""
        # Убираем лишние пробелы
        cron_expr = re.sub(r'\s+', ' ', cron_expr.strip())
        fields = cron_expr.split(' ')

        # Определяем количество полей и дополняем при необходимости
        if len(fields) == 5:
            # 5 полей: добавляем секунды и год
            fields = ['0'] + fields + ['*']
        elif len(fields) == 6:
            # 6 полей: добавляем год
            fields = fields + ['*']
        elif len(fields) == 7:
            # 7 полей: уже ок
            pass
        else:
            raise ValueError(f"Неподдерживаемый формат cron. Должно быть 5, 6 или 7 полей, получено {len(fields)}")

        return fields

    def _parse_field(self, field: str, min_val: int, max_val: int, is_second: bool = False) -> Set[int]:
        """Парсит одно поле cron"""
        # Специальные символы
        if field in ('*', '?', ''):
            return set(range(min_val, max_val + 1))

        # Заменяем текстовые значения
        field = self._replace_text_values(field)

        result = set()
        parts = field.split(',')

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Шаг (например */15)
            if '/' in part:
                range_part, step_part = part.split('/')
                step = int(step_part)

                # Определяем диапазон
                if range_part == '*' or range_part == '?':
                    start, end = min_val, max_val
                elif '-' in range_part:
                    start_str, end_str = range_part.split('-')
                    start, end = int(start_str), int(end_str)
                else:
                    # Одно значение
                    result.add(int(range_part))
                    continue

                # Добавляем значения с шагом
                for val in range(start, end + 1, step):
                    if min_val <= val <= max_val:
                        result.add(val)

            # Диапазон (например 1-5)
            elif '-' in part:
                start_str, end_str = part.split('-')
                start, end = int(start_str), int(end_str)
                for val in range(start, end + 1):
                    if min_val <= val <= max_val:
                        result.add(val)

            # Одно значение
            else:
                val = int(part)
                if min_val <= val <= max_val:
                    result.add(val)

        return result

    def _replace_text_values(self, field: str) -> str:
        """Заменяет текстовые названия месяцев и дней на числа"""
        # Месяцы
        for name, num in self.month_names.items():
            field = re.sub(rf'\b{name}\b', str(num), field, flags=re.IGNORECASE)

        # Дни недели
        for name, num in self.day_names.items():
            field = re.sub(rf'\b{name}\b', str(num), field, flags=re.IGNORECASE)

        return field


def get_next_cron_time(cron_expr: str) -> datetime:
    parser = UniversalCronParser()
    return parser.get_next_execution(cron_expr)

#
# sss = get_next_cron_time("0 0 0 * * * *")
# print(sss)