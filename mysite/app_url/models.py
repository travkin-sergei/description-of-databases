"""
class DimLin Обеспечивает уникальность ссылки url
"""
# app_url/models.py
import hashlib
from urllib.parse import urlparse
from django.db import models
from django.core.exceptions import ValidationError

from .apps import app
from _common.base_models import BaseClass


def normalize_url(url: str) -> str:
    """
    Нормализует URL для сравнения:
    - приводит к нижнему регистру,
    - убирает протокол (http/https),
    - убирает ведущее 'www.',
    - убирает завершающий '/',
    - убирает query и fragment (параметры и якоря).
    """
    if not url:
        return ''
    parsed = urlparse(url.lower().strip())

    # Убираем протокол
    netloc = parsed.netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # Собираем только схема-независимую часть: netloc + path (без query/fragment)
    path = parsed.path.rstrip('/') or ''  # удаляем завершающий слэш, но не делаем пустой путь None

    # Возвращаем нормализованную строку вида "example.com/path"
    return f"{netloc}{path}"


class DimUrl(BaseClass):
    url = models.URLField(max_length=2000, verbose_name='URL')
    url_normalized = models.CharField(
        max_length=2048,
        unique=True,
        db_index=True,
        editable=False,  # не редактируется вручную
        verbose_name='Нормализованный URL (для уникальности)'
    )
    url_hash = models.CharField(max_length=64, unique=True, db_index=True)
    login = models.CharField(max_length=128, blank=True, null=True, verbose_name='Логин')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='Пароль')
    status_code = models.IntegerField(blank=True, null=True, verbose_name='HTTP статус код')
    token = models.CharField(blank=True, null=True, verbose_name='token авторизации')

    class Meta:
        db_table = f'{app}\".\"dim_url'
        verbose_name = '001 Ссылка'
        verbose_name_plural = '001 Ссылки'
        ordering = ['url']

    def __str__(self):
        return self.url

    def clean(self):
        """Валидация на уровне модели — будет вызываться в forms.ModelForm и админке."""
        # Проверка дубликата по нормализованному URL (актуально при ручном создании)
        norm = normalize_url(self.url)
        if DimUrl.objects.filter(url_normalized=norm).exclude(pk=self.pk).exists():
            raise ValidationError({'url': 'Ссылка с таким адресом уже существует (после нормализации).'})

    def save(self, *args, **kwargs):
        # 1. Нормализуем URL
        self.url_normalized = normalize_url(self.url)

        # 2. Вычисляем хэш (например, SHA-256 от оригинального URL — если нужно хранить оригинал)
        # (Вы уже используете url_hash — убедитесь, что он тоже вычисляется, если не задан)
        if not self.url_hash:
            self.url_hash = hashlib.sha256(self.url.encode('utf-8')).hexdigest()

        # 3. Вызов clean() для валидации (опционально, но рекомендуется)
        self.full_clean()

        super().save(*args, **kwargs)
