# app_updates/models.py
from django.db import models
from app_dbm.models import LinkColumnColumn

from .apps import app
from _common.base_models import BaseClass


class DimUpdateMethod(BaseClass):
    """Методы обновления."""

    name = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.CharField(max_length=50, blank=True, null=True)
    link_code = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = f'{app}\".\"dim_update_method'
        verbose_name = '01 method update'
        verbose_name_plural = '01 method update'
        ordering = ['name']


class LinkUpdate(BaseClass):
    """Детали обновления для связи столбцов."""

    name = models.ForeignKey(
        DimUpdateMethod, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Метод обновления"
    )

    column = models.ForeignKey(
        LinkColumnColumn, on_delete=models.CASCADE, verbose_name='Связь столбцов'
    )

    def __str__(self):
        return f'{self.name}-{self.column}'

    class Meta:
        db_table = f'{app}"."link_update'
        unique_together = [['name', 'column']]
        verbose_name = '02 Детали обновления'
        verbose_name_plural = '02 Детали обновления'
        ordering = ['name']
