# app_updates/models.py
from django.db import models
from app_dbm.models import LinkColumnColumn
from app_url.models import DimUrl
from _common.base_models import BaseClass

from .apps import app


class DimUpdateMethod(BaseClass):
    """Методы обновления."""

    name = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.CharField(max_length=50, blank=True, null=True)
    url = models.ForeignKey(DimUrl, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = f'{app}\".\"dim_update_method'
        verbose_name = '01 метод обновления'
        verbose_name_plural = '01 методы обновлений'
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
