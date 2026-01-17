# app_updates/models.py
from django.db import models
from django.db.models import Q

from _common.models import BaseClass
from app_url.models import DimUrl
from app_dbm.models import LinkColumn

from .apps import db_schema


class DimUpdateMethod(BaseClass):
    name = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.CharField(max_length=50, blank=True, null=True)
    url = models.ForeignKey(DimUrl, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = f'{db_schema}"."dim_update_method'
        unique_together = [['name', 'schedule']]
        verbose_name = '01 метод обновления'
        verbose_name_plural = '01 методы обновлений'
        ordering = ['name', 'schedule']


class LinkUpdateCol(BaseClass):
    type = models.ForeignKey(DimUpdateMethod, on_delete=models.CASCADE)
    main = models.ForeignKey(LinkColumn, on_delete=models.CASCADE, related_name='update_main')
    sub = models.ForeignKey(LinkColumn, on_delete=models.CASCADE, related_name='update_sub', blank=True, null=True)

    def __str__(self):
        return f'{self.type}-{self.main}-{self.sub}'

    class Meta:
        db_table = f'{db_schema}"."link_update_col'
        unique_together = [['main', 'sub', 'type']]
        verbose_name = '02 обновление столбцов.'
        verbose_name_plural = '02 обновление столбцов.'
        ordering = ['main']
        constraints = [
            models.UniqueConstraint(
                fields=['main', 'sub', 'type'],
                name='unique_update_columns_relation'
            ),
        ]
        indexes = [
            models.Index(fields=['main']),
            models.Index(fields=['sub']),
            models.Index(fields=['type']),
        ]
