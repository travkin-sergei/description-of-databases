# app_url/models.py
"""
Модель DimUrl для хранения и нормализации URL с обеспечением уникальности.
"""

import hashlib
from urllib.parse import urlparse
from django.db import models
from django.core.exceptions import ValidationError
from _common.models import BaseClass
from .apps import db_schema


def normalize_url(url: str) -> str:
    """
    Нормализует URL для сравнения и обеспечения уникальности.

    Шаги нормализации:
    - Приведение к нижнему регистру.
    - Удаление протокола (http/https).
    - Удаление ведущего 'www.'.
    - Удаление завершающего '/'.
    - Исключение query и fragment (параметров и якорей).

    Args:
        url (str): Исходный URL.

    Returns:
        str: Нормализованный URL (например, 'example.com/path').
    """
    if not url:
        return ''

    parsed = urlparse(url.lower().strip())

    # Удаление протокола и обработка netloc
    netloc = parsed.netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # Обработка пути (удаление завершающего слэша)
    path = parsed.path.rstrip('/') or ''

    return f"{netloc}{path}"


class DimUrl(BaseClass):
    """
    Модель для хранения URL с нормализованным представлением и хэшем.

    Поля:
    - url: исходный URL.
    - url_normalized: нормализованный URL для проверки уникальности.
    - url_hash: хэш URL для быстрого поиска.
    - login/password: учётные данные для аутентификации.
    - status_code: HTTP‑статус ответа.
    - token: токен авторизации.
    """
    url = models.URLField(max_length=2000, verbose_name='URL')
    url_normalized = models.CharField(
        max_length=2048, unique=True, db_index=True, editable=False,
        verbose_name='Нормализованный URL (для уникальности)'
    )
    url_hash = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='Хэш URL')
    login = models.CharField(max_length=128, blank=True, null=True, verbose_name='Логин')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='Пароль')
    status_code = models.IntegerField(blank=True, null=True, verbose_name='HTTP статус код')
    token = models.CharField(max_length=255, blank=True, null=True, verbose_name='Токен авторизации')

    class Meta:
        db_table = f'{db_schema}"."dim_url'
        verbose_name = '001 Ссылка'
        verbose_name_plural = '001 Ссылки'
        ordering = ['url']

    def __str__(self):
        """Строковое представление объекта (используется в админке и др.)."""
        return self.url

    def clean(self):
        """
        Валидация на уровне модели.

        Проверяет уникальность нормализованного URL (исключая текущий объект при обновлении).
        Вызывается автоматически в ModelForm и админке.
        """
        norm = normalize_url(self.url)
        if (DimUrl.objects
                .filter(url_normalized=norm)
                .exclude(pk=self.pk)
                .exists()):
            raise ValidationError({
                'url': 'Ссылка с таким адресом уже существует (после нормализации).'
            })

    def save(self, *args, **kwargs):
        """
        Переопределённый метод save() для автоматической нормализации и хэширования.

        Шаги:
        1. Нормализация URL и заполнение url_normalized.
        2. Вычисление хэша (если не задан).
        3. Валидация через full_clean().
        4. Сохранение объекта.
        """
        # Нормализация URL
        self.url_normalized = normalize_url(self.url)

        # Вычисление хэша (если отсутствует)
        if not self.url_hash:
            self.url_hash = hashlib.sha256(self.url.encode('utf-8')).hexdigest()

        # Валидация
        self.full_clean()

        super().save(*args, **kwargs)
