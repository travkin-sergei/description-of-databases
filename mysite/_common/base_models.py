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
    """Пагинатор с ограничением максимального количества записей"""
    max_limit = 1000  # или другое значение

    def page(self, number):
        number = self.validate_number(number)
        # Ограничиваем смещение
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top > self.max_limit:
            top = self.max_limit
        if bottom > self.max_limit:
            bottom = self.max_limit - self.per_page
        return self._get_page(self.object_list[bottom:top], number, self)
