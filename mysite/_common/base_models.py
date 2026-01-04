# _common/base_models.py
"""
Общие классы и методы всех приложений проекта
"""
import hashlib
from typing import List, Union

from django.core.paginator import Paginator
from django.db import models


def hash_calculate(fields_array: List[Union[str, int, float, None]]) -> str:
    """
    Универсальная функция для расчета хэша из массива.

    Args:
        fields_array: list - массив значений для хэширования

    Returns:
        str: SHA-256 хэш в hex формате
    """
    # Проверка входных данных
    if not isinstance(fields_array, (list, tuple)):
        raise TypeError("fields_array должен быть list или tuple")

    # Преобразование в строки
    string_fields = []
    for field in fields_array:
        if field is None:
            string_fields.append('')
        else:
            string_fields.append(str(field))
    # Объединение и хэширование
    hash_string = '|'.join(string_fields)
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()


class BaseClass(models.Model):
    """
    Абстрактная базовая модель, содержащая общие поля для всех моделей.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    is_active = models.BooleanField(default=True, verbose_name='запись активна')

    class Meta:
        abstract = True


class SafePaginator(Paginator):
    """
    Paginator, который ограничивает QuerySet до max_limit записей на уровне SQL.
    Отказывается от точного .count(), если общее число > max_limit.
    """
    max_limit = 1000

    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        # Если object_list — QuerySet, ограничиваем его сразу
        if isinstance(object_list, models.QuerySet):
            # Обязательно должен быть order_by — иначе LIMIT недетерминирован
            if not object_list.query.order_by:
                object_list = object_list.order_by('pk')

            # Берём max_limit + 1, чтобы определить, нужно ли резать
            object_list = object_list[:self.max_limit + 1]

        super().__init__(object_list, per_page, orphans, allow_empty_first_page)

    @property
    def count(self):
        """
        Возвращает реальное количество элементов в ограниченном списке.
        Не делает COUNT(*), а использует len() на уже ограниченном QuerySet или списке.
        """
        if isinstance(self.object_list, models.QuerySet):
            # len(QuerySet) → делает SELECT COUNT(*) LIMIT N+1? Нет!
            # На самом деле: len(qs[:N]) → делает SELECT ... LIMIT N и подсчитывает в памяти.
            # ✅ Это быстро, т.к. LIMIT уже в запросе.
            return len(self.object_list)
        else:
            return len(self.object_list)

    def page(self, number):
        number = self.validate_number(number)

        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page

        # Уже ограниченный object_list (≤ max_limit + 1)
        limited_list = list(self.object_list)  # materialize once
        self._is_limited = len(limited_list) > self.max_limit
        if self._is_limited:
            limited_list = limited_list[:self.max_limit]

        # Обрезаем под текущую страницу
        page_items = limited_list[bottom:top]

        return self._get_page(page_items, number, self)

    @property
    def is_limited(self):
        # Вызывается после page(), т.к. _is_limited устанавливается там
        return getattr(self, '_is_limited', False)
