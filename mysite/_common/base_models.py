# _common/base_models.py
"""
Общие классы и методы всех приложений проекта
"""
import hashlib
from typing import List, Union
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
