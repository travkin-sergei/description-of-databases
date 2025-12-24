# app_request/models.py
from django.db import models

from app_dbm.models import LinkColumn

db_schema = 'app_request'


class BaseClass(models.Model):
    """"
    Абстрактная базовая модель, содержащая общие поля для всех моделей.
    Attributes:
        created_at (DateTime): Дата и время создания записи (автоматически устанавливается).
        updated_at (DateTime): Дата и время последнего обновления записи (автоматически обновляется).
        is_active (Boolean): Флаг активности записи (по умолчанию True).
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    is_active = models.BooleanField(default=True, verbose_name='запись активна')

    class Meta:
        abstract = True


class ColumnGroupName(BaseClass):
    """Название группировок столбцов"""
    name = models.CharField(max_length=255, verbose_name='Номер закона')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_group_name'
        unique_together = [["name"]]
        verbose_name = '01 название групп столбцов.'
        verbose_name_plural = '01 названия групп столбцов.'


class ColumnGroup(BaseClass):
    """
    Список столбцов таблиц и их группировка
    """
    column = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, )
    group_name = models.ForeignKey(ColumnGroupName, on_delete=models.PROTECT, )

    def __str__(self):
        return f'{self.column}-{self.group_name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_column_group_name'
        unique_together = [["column", "group_name"]]
        verbose_name = '02 группа столбцов.'
        verbose_name_plural = '02 группы столбцов.'
