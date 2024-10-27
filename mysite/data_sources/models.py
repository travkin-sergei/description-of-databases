from django.db import models

"""
Модель данных списка источников данных
"""


class Base(models.Model):
    """
    Базовая модель проекта
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    is_active = models.BooleanField(default=True, verbose_name='запись активна')
    task = models.URLField(verbose_name='Cсылка на задачу в Jira')

    class Meta:
        abstract = True


class DataSources(Base):
    """
    Список источников данных
    """
    slag = models.CharField(max_length=25, primary_key=True)
    link_sources = models.URLField(blank=True, null=True)
    doc_regulatory = models.URLField(blank=True, null=True)
    name_sources = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.slag

    class Meta:
        db_table = 'source_data'
        verbose_name = '01 Список источников'
        verbose_name_plural = '01 Список источников'
