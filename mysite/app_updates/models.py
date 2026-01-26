# app_updates/models.py
from django.db import models
from django.db.models import Q, Index

from _common.models import BaseClass
from app_url.models import DimUrl
from app_dbm.models import LinkColumn

from .apps import db_schema


class DimUpdateMethod(BaseClass):
    """
    Модель, описывающая методы обновления данных.

    Поля:
    - name: название метода (до 255 символов, может быть пустым).
    - schedule: расписание выполнения (до 50 символов, может быть пустым).
    - url: внешняя ссылка на источник/документацию (связь с DimUrl).
    """

    name = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='Название метода'
    )
    schedule = models.CharField(
        max_length=50, blank=True, null=True,
        verbose_name='Расписание'
    )
    url = models.ForeignKey(
        DimUrl, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Ссылка на источник'
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name='Описание расписания.'
    )

    def __str__(self):
        return self.name or 'Без названия'

    class Meta:
        db_table = f'{db_schema}"."dim_update_method'
        unique_together = [['name', 'schedule']]
        verbose_name = '01 Метод обновления'
        verbose_name_plural = '01 Методы обновлений'
        ordering = ['name', 'schedule']
        indexes = [
            Index(fields=['name']),
            Index(fields=['schedule']),
        ]


class LinkUpdateCol(BaseClass):
    """
    Модель связи метода обновления с колонками (LinkColumn).

    Поля:
    - type: связь с методом обновления (DimUpdateMethod).
    - main: основная колонка (LinkColumn).
    - sub: дополнительная колонка (LinkColumn, может отсутствовать).
    """
    type = models.ForeignKey(
        DimUpdateMethod, on_delete=models.CASCADE,
        verbose_name='Метод обновления'
    )
    main = models.ForeignKey(
        LinkColumn, on_delete=models.CASCADE,
        related_name='update_main', verbose_name='Основная колонка'
    )
    sub = models.ForeignKey(
        LinkColumn, on_delete=models.CASCADE, related_name='update_sub', blank=True, null=True,
        verbose_name='Дополнительная колонка'
    )

    def __str__(self):
        main_str = self.main.pk if self.main else 'N/A'
        sub_str = self.sub.pk if self.sub else 'N/A'
        type_str = self.type.name or self.type.pk
        return f'{type_str} ({main_str} → {sub_str})'

    class Meta:
        db_table = f'{db_schema}"."link_update_col'
        unique_together = [['main', 'sub', 'type']]
        verbose_name = '02 Обновление столбцов'
        verbose_name_plural = '02 Обновления столбцов'
        ordering = ['main']
        constraints = [
            models.UniqueConstraint(
                fields=['main', 'sub', 'type'],
                name='unique_update_columns_relation'
            ),
        ]
        indexes = [
            Index(fields=['main']),
            Index(fields=['sub']),
            Index(fields=['type']),
        ]
