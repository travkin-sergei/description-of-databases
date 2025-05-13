import hashlib

from django.db import models
from django.db.models.signals import pre_save

db_schema = 'my_metla'


class BaseModel(models.Model):
    """Созданы базовые поля, важные для всех таблиц."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')
    hash_address = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True, verbose_name='запись активна')

    def hash_sum_256(self, args):
        """
        Сгенерируйте хэш SHA-256 из предоставленных аргументов.

        Аргументы:
            args: Список значений, которые необходимо включить в расчет хэша

        Возвращается:
            str: шестнадцатеричный дайджест хэша
        """
        list_str = [str(i) for i in args]
        list_union = '+'.join(list_str)
        return hashlib.sha256(list_union.encode()).hexdigest()

    def get_hash_fields(self):
        """
        Получить список полей для включения в расчет хэша.
        Должно быть реализовано в дочерних классах.
        """
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """Сохранение с автоматической генерацией хэша."""
        pre_save.send(sender=self.__class__, instance=self, request=kwargs.get('request'))
        self.hash_address = self.hash_sum_256(self.get_hash_fields())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseType(BaseModel):
    """Типы баз данных."""

    name = models.CharField(max_length=10, verbose_name='Тип баз данных')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"src_base_type'
        verbose_name = '0100 Тип базы данных'
        verbose_name_plural = '0100 Типы баз данных'
        ordering = ['name']


class Base(BaseModel):
    """База данных."""

    type = models.ForeignKey(BaseType, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.name, self.host]

    def __str__(self):
        return f'{self.type}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"src_bases'
        verbose_name = '0101 База данных'
        verbose_name_plural = '0101 Базы данных'
        ordering = ['name', 'type']
        unique_together = [['name', 'type']]


class Schema(BaseModel):
    """Схема базы данных."""
    name = models.CharField(max_length=150)

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"src_schema'
        verbose_name = '0201 Схема'
        verbose_name_plural = '0201 Схемы'
        ordering = ['name']


class TableType(BaseModel):
    """Типы таблиц."""
    name = models.CharField(max_length=10, verbose_name='Тип таблицы')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"src_table_type'
        verbose_name = '0300 Тип таблицы'
        verbose_name_plural = '0300 Типы таблиц'
        ordering = ['name']


class Table(BaseModel):
    """Таблицы базы данных."""
    name = models.CharField(max_length=150, verbose_name='Название в БД')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"src_tables'
        verbose_name = '0301 Список таблиц'
        verbose_name_plural = '0301 Список таблиц'
        ordering = ['name']


class ColumnType(BaseModel):
    """Типы столбцов."""
    name = models.CharField(max_length=10, verbose_name='Тип столбца')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"src_column_type'
        verbose_name = '0400 Тип столбца'
        verbose_name_plural = '0400 Типы столбцов'
        ordering = ['name']


class Column(BaseModel):
    """Колонки таблиц."""

    type = models.ForeignKey(ColumnType, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название столбца')
    is_nullable = models.BooleanField(blank=True, null=True)
    is_auto = models.BooleanField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.type, self.name]

    def __str__(self):
        return f'{self.type}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"src_columns'
        verbose_name = '0401 Столбец'
        verbose_name_plural = '0401 Столбцы'
        ordering = ['type', 'name']
        unique_together = [['type', 'name']]


class BaseSchema(BaseModel):
    """Список схем базы данных."""

    base = models.ForeignKey(Base, on_delete=models.CASCADE, blank=True, null=True)
    schema = models.ForeignKey(Schema, on_delete=models.PROTECT, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.base, self.schema]

    def __str__(self):
        return f'{self.base}-{self.schema}'

    class Meta:
        db_table = f'{db_schema}\".\"link_base_schema'
        verbose_name = '1000 База-схема'
        verbose_name_plural = '1000 Базы-схемы'
        ordering = ['base']
        unique_together = [['base', 'schema']]


class SchemaTable(BaseModel):
    """Свод данных."""

    base_schema = models.ForeignKey(BaseSchema, on_delete=models.CASCADE, blank=True, null=True)
    table_is_metadata = models.BooleanField(default=False, verbose_name='Таблица метаданных')
    table_type = models.ForeignKey(TableType, on_delete=models.CASCADE, blank=True, null=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.base_schema, self.table]

    def __str__(self):
        return f'{self.base_schema}-{self.table_is_metadata}-{self.table_type}-{self.table}'

    class Meta:
        db_table = f'{db_schema}\".\"link_schema_table'
        verbose_name = '2000 схема-таблица.'
        verbose_name_plural = '2000 схемы-таблицы.'
        ordering = ['table']
        unique_together = [['base_schema', 'table']]


class TableColumn(BaseModel):
    """Свод данных."""

    schema_table = models.ForeignKey(SchemaTable, on_delete=models.CASCADE, blank=True, null=True)
    numbers = models.PositiveIntegerField(blank=True, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.schema_table, self.column]

    def __str__(self):
        return f'{self.schema_table} - {self.column}'

    class Meta:
        db_table = f'{db_schema}\".\"link_table_column'
        verbose_name = '3000 таблица-столбец.'
        verbose_name_plural = '3000 таблицы-столбецы.'
        ordering = ['numbers', ]
        unique_together = [['schema_table', 'column', ]]

