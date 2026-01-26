# app_dict/models.py
from django.db import models
from .apps import db_schema
from _common.models import BaseClass


class DimCategory(BaseClass):
    """Категории"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_category'
        unique_together = [["name"]]
        verbose_name = '01 Категории'
        verbose_name_plural = '01 Категории'
        ordering = ['name']


class DimDictionary(BaseClass):
    """Словарь."""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(DimCategory, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_dictionary'  # Исправлено
        unique_together = [["name", "category"]]
        verbose_name = '02 Словарь'
        verbose_name_plural = '02 Словарь'
        ordering = ['name']


class LinkDictionaryName(BaseClass):
    """Синонимы названий слов."""
    name = models.ForeignKey(
        DimDictionary,
        on_delete=models.PROTECT,
        related_name="synonyms"
    )
    synonym = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}-{self.synonym}'

    class Meta:
        db_table = f"{db_schema}'.'link_dictionary"
        unique_together = [['name', 'synonym']]
        verbose_name = '03 Связь столбцов и синонимов'
        verbose_name_plural = '03 Связь столбцов и синонимов'
        ordering = ['name']
