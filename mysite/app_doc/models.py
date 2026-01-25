# app_doc/models.py
from django.db import models
from _common.models import BaseClass
from app_url.models import DimUrl
from .apps import db_schema


class DimDocType(BaseClass):
    """Простая таблица типов документов"""
    name = models.CharField(max_length=255, verbose_name='Название типа')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'"{db_schema}"."dim_doc_type"'
        verbose_name = '001 Тип документа'
        verbose_name_plural = '001 Типы документов'


class DimDoc(BaseClass):
    """Простая таблица документов"""
    doc_type = models.ForeignKey(DimDocType, on_delete=models.PROTECT, verbose_name='Тип')
    number = models.CharField(max_length=250, verbose_name='Название')
    date_start = models.DateField(blank=True, null=True, verbose_name='Дата вступления в силу', )
    date_stop = models.DateField(blank=True, null=True, verbose_name='Дата прекращения действия', )
    link = models.ForeignKey(DimUrl, blank=True, null=True, on_delete=models.PROTECT, verbose_name='Ссылка')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        if self.date_start:
            return f'{self.number} от {self.date_start.strftime("%Y-%m-%d")}'
        return f'{self.number} (без даты)'

    class Meta:
        db_table = f'"{db_schema}"."dim_doc"'
        unique_together = [['doc_type', 'number', 'date_start']]
        verbose_name = '002 Документ'
        verbose_name_plural = '002 Документы'
        ordering = ['date_start', 'date_stop', 'number']
