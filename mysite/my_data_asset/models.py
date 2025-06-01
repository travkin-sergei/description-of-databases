from django.db import models
from django.db.models.functions import Now

from dba.models import Table

db_schema = 'my_data_asset'


class SystemColumns(models.Model):
    """Набор минимальных системных столбцов."""

    created_at = models.DateTimeField(
        db_default=Now()
        , verbose_name='Создано'
        , help_text="Создано"

    )
    updated_at = models.DateTimeField(
        db_default=Now()
        , verbose_name='Обновлено'
        , help_text="Обновлено"

    )
    is_active = models.BooleanField(
        db_default=True
        , verbose_name='Запись активна?'
        , help_text="Запись активна?"
    )

    class Meta:
        abstract = True


class BaseModel(SystemColumns):
    """Базовая модель приложения Asset."""

    hash_address = models.CharField(
        max_length=64, blank=True, null=True
        , db_comment='{'
                     '"name":"Хеш адрес строки",'
                     '"description":"Алгоритм sha256. Важно соблюдать регистр и порядок.",'
                     '}'
        , help_text="Алгоритм sha256. Важно соблюдать регистр и порядок.",
    )
    task = models.CharField(
        max_length=64, blank=True, null=True
        , db_comment='{'
                     '"name":"Задача, в рамках которой появилась запись.",'
                     '"description":"Имеется в виду не в этой базе данных, а в источнике, если это применимо.",'
                     ',}'
        , help_text="Алгоритм sha256. Важно соблюдать регистр и порядок.",
    )

    class Meta:
        abstract = True


class AssetType(BaseModel):
    """Типа"""

    name = models.CharField(
        primary_key=True
        , max_length=255
        , verbose_name="Тип данных."
        , db_comment='{"name":"Тип данных.",}'
        , help_text="Тип данных.",
    )
    description = models.CharField(
        blank=True, null=True
        , verbose_name="Описание."
        , db_comment='{"name":"Описание.",}'
        , help_text="Тип данных.",
    )

    def __str__(self):
        return f'{self.name}' or 'NO DATA'

    class Meta:
        managed = True
        db_table = f'{db_schema}\".\"asset_type'  # Указываем имя таблицы в базе данных
        ordering = ['name']  # Сортировка по дате создания (по убыванию)
        unique_together = (('name',),)
        verbose_name = '010 Тип'  # Указываем имя таблицы в админке
        verbose_name_plural = '010 Типы'  # Указываем имя таблицы в админке


class AssetDomain(BaseModel):
    """Типа"""

    name = models.CharField(
        primary_key=True
        , max_length=255
        , verbose_name="Домен данных."
        , db_comment='{"name":"Домен данных.",}'
        , help_text="Домен данных.",
    )
    description = models.CharField(
        blank=True, null=True
        , verbose_name="Описание."
        , db_comment='{"name":"Описание.",}'
        , help_text="Тип данных.",
    )
    res_url = models.URLField(
        blank=True, null=True
        , verbose_name="Ссылка на ресурс."
        , db_comment='{"name":"Ссылка на ресурс.",}'
        , help_text="Ссылка на ресурс",
    )

    def __str__(self):
        return f'{self.name}' or 'NO DATA'

    class Meta:
        managed = True
        db_table = f'{db_schema}\".\"asset_domain'  # Указываем имя таблицы в базе данных
        ordering = ['name']  # Сортировка по дате создания (по убыванию)
        unique_together = (('name',),)
        verbose_name = '020 Домен'  # Указываем имя таблицы в админке
        verbose_name_plural = '020 Домены'  # Указываем имя таблицы в админке


class AssetDetails(BaseModel):
    """Типа"""

    name = models.CharField(
        primary_key=True
        , max_length=255
        , verbose_name="Детализация данных."
        , db_comment='{"name":"Детализация данных.",}'
        , help_text="Детализация данных.",
    )
    description = models.CharField(
        blank=True, null=True
        , verbose_name="Описание."
        , db_comment='{"name":"Описание.",}'
        , help_text="Тип данных.",
    )

    def __str__(self):
        return f'{self.name}' or 'NO DATA'

    class Meta:
        managed = True
        db_table = f'{db_schema}\".\"asset_details'  # Указываем имя таблицы в базе данных
        ordering = ['name']  # Сортировка по дате создания (по убыванию)
        unique_together = (('name',),)
        verbose_name = '030 Детализация'  # Указываем имя таблицы в админке
        verbose_name_plural = '030 Детализация'  # Указываем имя таблицы в админке


class Asset(BaseModel):
    """Статистка источника данных."""

    table = models.OneToOneField(
        Table,
        on_delete=models.CASCADE,
        related_name='extension',
        verbose_name='Таблица'
    )
    type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    domain = models.ForeignKey(AssetDomain, on_delete=models.CASCADE)
    details = models.ForeignKey(AssetDetails, on_delete=models.CASCADE)
    version = models.CharField(
        max_length=255
        , verbose_name="Версия данных."
        , db_comment='{"name":"Версия данных.",}'
        , help_text="Версия данных.",
    )
    description = models.CharField(
        blank=True, null=True
        , max_length=255
        , verbose_name="Описание."
        , db_comment='{"name":"Описание.",}'
        , help_text="Описание",
    )
    res_url = models.URLField(
        blank=True, null=True
        , verbose_name="Ссылка на ресурс."
        , db_comment='{"name":"Ссылка на ресурс.",}'
        , help_text="Ссылка на ресурс",
    )
    docs_url = models.URLField(
        blank=True, null=True
        , verbose_name="Нормативная документация."
        , db_comment='{"name":"Нормативная документация.",}'
        , help_text="Нормативная документация.",
    )
    last_update = models.DateTimeField(blank=True, null=True)
    total_row = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = f'{db_schema}\".\"ssssss'
        verbose_name = 'Расширение таблицы'
        verbose_name_plural = 'Расширения таблиц'

    def __str__(self):
        return f'Доп. данные для {self.table}'
