# app_doc/models.py
"""
Приложение по систематизации документов.
"""

from django.db import models
from _common.base_models import BaseClass
from app_url.models import DimUrl

from .apps import app


class DimDocType(BaseClass):
    """Простая таблица типов документов"""

    name = models.CharField(max_length=255, verbose_name='Название типа')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{app}\".\"dim_doc_type'
        verbose_name = '001 Тип документа'
        verbose_name_plural = '001 Типы документов'


class DimDoc(BaseClass):
    """Простая таблица документов"""

    doc_type = models.ForeignKey(DimDocType, on_delete=models.PROTECT, verbose_name='Тип')
    number = models.CharField(max_length=250, verbose_name='Название')
    date_start = models.DateField(verbose_name='Дата вступления в силу',blank=True, null=True,)
    date_stop = models.DateField(verbose_name='Дата прекращения действия',blank=True, null=True,)
    link = models.ForeignKey(DimUrl, on_delete=models.PROTECT,blank=True, null=True,)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        date_str = self.date_start.strftime('%Y-%m-%d')
        return f'{self.number} от {date_str}'

    class Meta:
        db_table = f'{app}\".\"dim_doc'
        verbose_name = '002 Документ'
        verbose_name_plural = '002 Документы'
