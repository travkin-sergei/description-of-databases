# app_request/models.py
from django.db import models
from app_dbm.models import LinkColumn, LinkTable
from _common.models import BaseClass
from .apps import db_schema


class TableGroupName(BaseClass):
    """Название группировок таблиц"""
    name = models.CharField(max_length=255, verbose_name='Имя таблицы')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'"{db_schema}"."dim_table_group"'
        unique_together = [['name']]
        verbose_name = '01 Название групп таблиц'
        verbose_name_plural = '01 Названия групп таблиц'


class TableGroup(BaseClass):
    """Список таблиц и их группировка"""
    table = models.ForeignKey(
        LinkTable,
        on_delete=models.PROTECT,
        verbose_name='Таблица'
    )
    group_name = models.ForeignKey(
        TableGroupName,
        on_delete=models.PROTECT,
        verbose_name='Группа'
    )

    def __str__(self):
        return f'{self.table} — {self.group_name}'

    class Meta:
        db_table = f'"{db_schema}"."link_table_group"'
        unique_together = [['table', 'group_name']]
        verbose_name = '02 Группа таблиц'
        verbose_name_plural = '02 Группы таблиц'


class ColumnGroupName(BaseClass):
    """Название группировок столбцов"""
    name = models.CharField(max_length=255, verbose_name='Номер закона')

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'"{db_schema}"."dim_columns_group"'
        unique_together = [['name']]
        verbose_name = '03 Название групп столбцов'
        verbose_name_plural = '03 Названия групп столбцов'


class ColumnGroup(BaseClass):
    """Список столбцов таблиц и их группировка"""
    column = models.ForeignKey(
        LinkColumn,
        on_delete=models.PROTECT,
        verbose_name='Столбец'
    )
    group_name = models.ForeignKey(
        ColumnGroupName,
        on_delete=models.PROTECT,
        verbose_name='Группа столбцов'
    )

    def __str__(self):
        return f'{self.column} — {self.group_name}'

    class Meta:
        db_table = f'"{db_schema}"."link_column_group"'
        unique_together = [['column', 'group_name']]
        verbose_name = '04 Группа столбцов'
        verbose_name_plural = '04 Группы столбцов'
