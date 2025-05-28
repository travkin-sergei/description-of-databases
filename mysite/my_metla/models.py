import hashlib

from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone

db_schema = 'my_metla'


# общие поля для всех моделей
class BaseModel(models.Model):
    """
    Базовые поля для всех моделей:
      - created_at: дата и время создания записи (заполняется при first save)
      - updated_at: дата и время последнего изменения (обновляется при каждом save)
      - is_active: флаг активности записи
      - hash_address: вычисляемое поле-хэш (если нужно)
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_default=timezone.now(),
        verbose_name='дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_default=timezone.now(),
        verbose_name='дата изменения'
    )
    is_active = models.BooleanField(
        default=True,
        db_default=True,
        verbose_name='запись активна'
    )

    # hash_address = models.CharField(
    #     max_length=64,
    #     editable=False,
    #     blank=True,
    #     verbose_name='хэш адреса'
    # )

    def hash_sum_256(self, args):
        list_union = '+'.join(str(i) for i in args)
        return hashlib.sha256(list_union.encode()).hexdigest()

    def get_hash_fields(self):
        """
        Переопределяется в каждой дочерней модели,
        возвращает список полей, по которым считаем хэш.
        """
        raise NotImplementedError

    def save(self, *args, **kwargs):
        # Перед сохранением пересчитаем хэш
        try:
            fields = self.get_hash_fields()
            self.hash_address = self.hash_sum_256(fields)
        except NotImplementedError:
            pass
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


# Среды разработки
class Environment(BaseModel):
    """Переменное окружение."""

    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_environment'
        verbose_name = '0010 Среда разработки'
        verbose_name_plural = '0010 Среды разработки'
        ordering = ['pk']


# Названия баз данных
class BaseName(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return f'{self.name}'

    def get_hash_fields(self):
        return [self.name]  # или другие поля, если они есть

    class Meta:
        db_table = f'{db_schema}\".\"dim_base_name'
        verbose_name = '0011 Имена баз данных'
        verbose_name_plural = '0011 Имена баз данных'
        ordering = ['name']


# Типы баз данных
class BaseType(BaseModel):
    """Типы баз данных."""

    name = models.CharField(max_length=255, verbose_name='Тип баз данных')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_base_type'
        verbose_name = '0010 Типы баз данных'
        verbose_name_plural = '0010 Типы баз данных'
        ordering = ['name']


# База данных (хост, порт)
class Base(BaseModel):
    """Базы данных."""

    name = models.ForeignKey(BaseName, on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(BaseType, on_delete=models.CASCADE, blank=True, null=True)
    host_name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.name, self.host, self.port]

    def __str__(self):
        return f'{self.host_name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_bases'
        verbose_name = '0012 База'
        verbose_name_plural = '0012 Базы'
        ordering = ['name', 'host', 'port']
        unique_together = [['name', 'host', 'port']]


# Список Алиасов названий баз
class SchemAlias(BaseModel):
    """Алиас схем."""

    name = models.CharField(max_length=255, verbose_name='Алиас схем')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_schem_alias'
        verbose_name = '0100 Alias Schem'
        verbose_name_plural = '0100 Alias Schem'
        ordering = ['name']


# Список названий схем
class SchemesName(BaseModel):
    """Типы баз данных."""

    name = models.CharField(max_length=255, verbose_name='Тип баз данных')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_schema_name'
        verbose_name = '0013 название схемы'
        verbose_name_plural = '0013 название схем'
        ordering = ['name']


class Schemas(BaseModel):
    """База-схема-алиас."""

    base = models.ForeignKey(Base, on_delete=models.CASCADE, )
    schema = models.ForeignKey(SchemesName, on_delete=models.CASCADE, )
    alias = models.ForeignKey(SchemAlias, on_delete=models.CASCADE, blank=True, null=True)
    env = models.ForeignKey(Environment, on_delete=models.CASCADE, blank=True, null=True)

    def get_hash_fields(self):
        return [self.base, self.schema]

    def __str__(self):
        return f'{self.base} - {self.schema}'

    class Meta:
        db_table = f'{db_schema}\".\"link_base_alias'
        verbose_name = 'Schemas таблица-столбец.'
        verbose_name_plural = 'Schemas таблицы-столбецы'
        ordering = ['base', 'alias', 'schema']
        unique_together = [['base', 'schema', ]]


class TableType(BaseModel):
    """Типы таблиц."""

    name = models.CharField(max_length=255, verbose_name='Тип таблицы')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_table_type'
        verbose_name = '0300 Тип таблицы'
        verbose_name_plural = '0300 Типы таблиц'
        ordering = ['name']


class TableName(BaseModel):
    """Таблицы базы данных."""

    name = models.CharField(max_length=255, verbose_name='Название в БД')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_table_name'
        verbose_name = '0301 Список таблиц'
        verbose_name_plural = '0301 Список таблиц'
        ordering = ['name']


class SchemaTable(BaseModel):
    """Свод данных."""

    schemas = models.ForeignKey(Schemas, on_delete=models.CASCADE, blank=True, null=True)
    table = models.ForeignKey(TableName, on_delete=models.CASCADE, blank=True, null=True)
    table_type = models.ForeignKey(TableType, on_delete=models.CASCADE, blank=True, null=True)
    table_is_metadata = models.BooleanField(default=False, verbose_name='Таблица метаданных')
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.schemas, self.table,self.table_type]

    def __str__(self):
        return f'{self.table}-{self.table_type}'

    class Meta:
        db_table = f'{db_schema}\".\"link_table'
        verbose_name = '2000 схема-таблица.'
        verbose_name_plural = '2000 схемы-таблиц'
        ordering = ['schemas', 'table']
        unique_together = [['schemas', 'table', 'table_type',]]


class ColumnType(BaseModel):
    """Типы столбцов."""

    name = models.CharField(max_length=255, verbose_name='Тип столбца')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_column_type'
        verbose_name = '0400 Тип столбца'
        verbose_name_plural = '0400 Типы столбцов'
        ordering = ['name']


class ColumnName(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название столбца')

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_column_name'
        verbose_name = '0401 Имена столбца'
        verbose_name_plural = '0401 Имена столбцов'
        ordering = ['name']


class Column(BaseModel):
    """Свод данных."""

    table = models.ForeignKey(SchemaTable, on_delete=models.CASCADE, blank=True, null=True)
    numbers = models.PositiveIntegerField(blank=True, null=True)
    name = models.ForeignKey(ColumnName, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Имя')
    type = models.ForeignKey(ColumnType, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Тип данных')
    is_nullable = models.BooleanField(default=True, blank=True, verbose_name='Возможен ли ноль', )
    is_auto = models.BooleanField(default=False, blank=True, verbose_name='Автоматическое заполнение', )
    description = models.TextField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.table, self.name]

    def __str__(self):
        return f'{self.table} - {self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_column'
        verbose_name = '3000 таблица-столбец.'
        verbose_name_plural = '3000 таблицы-столбецы'
        ordering = ['numbers', ]
        unique_together = [['table', 'name', ]]
