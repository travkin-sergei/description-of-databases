# app_request/models.py
from django.db import models

from app_dbm.models import LinkColumn

from .apps import app
from _common.base_models import BaseClass


class TableGroupName(BaseClass):
    """Название группировок таблиц"""
    name = models.CharField(max_length=255, verbose_name='Имя таблицы')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{app}\".\"dim_table_group'
        unique_together = [["name"]]
        verbose_name = '01 название групп таблиц.'
        verbose_name_plural = '01 названия групп таблиц.'


class TableGroup(BaseClass):
    """
    Список таблиц и их группировка
    """
    table = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, )
    group_name = models.ForeignKey(TableGroupName, on_delete=models.PROTECT, )

    def __str__(self):
        return f'{self.table}-{self.group_name}'

    class Meta:
        db_table = f'{app}\".\"link_table_group'
        unique_together = [["table", "group_name"]]
        verbose_name = '02 группа таблиц.'
        verbose_name_plural = '02 группы таблиц.'


class ColumnGroupName(BaseClass):
    """Название группировок столбцов"""
    name = models.CharField(max_length=255, verbose_name='Номер закона')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{app}\".\"dim_columns_group'
        unique_together = [["name"]]
        verbose_name = '03 название групп столбцов.'
        verbose_name_plural = '03 названия групп столбцов.'


class ColumnGroup(BaseClass):
    """
    Список столбцов таблиц и их группировка
    """
    column = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, )
    group_name = models.ForeignKey(ColumnGroupName, on_delete=models.PROTECT, )

    def __str__(self):
        return f'{self.column}-{self.group_name}'

    class Meta:
        db_table = f'{app}\".\"link_column_group'
        unique_together = [["column", "group_name"]]
        verbose_name = '04 группа столбцов.'
        verbose_name_plural = '03 группы столбцов.'
