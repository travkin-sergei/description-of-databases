import datetime

from django.db import models

db_schema = 'my_dbmatch'


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


class DimStage(BaseClass):
    """Справочник стендов разработки."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_stage'
        unique_together = [["name"]]
        verbose_name = '01 Словарь слоев.'
        verbose_name_plural = '01 Словарь слоев.'


class DimDB(BaseClass):
    """ Справочник баз данных."""

    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.version}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_db'
        unique_together = [['name', ]]
        verbose_name = '03 Словарь баз данных.'
        verbose_name_plural = '03 Словарь баз данных.'


class LinkDB(BaseClass):
    """ Справочник баз данных."""

    data_base = models.ForeignKey(DimDB, on_delete=models.PROTECT)
    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    stage = models.ForeignKey(DimStage, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} ({self.host})"

    class Meta:
        db_table = f'{db_schema}\".\"link_db'
        unique_together = [['name', 'host', 'port', ]]
        verbose_name = '04 Список баз данных.'
        verbose_name_plural = '04 Список баз данных.'


class LinkDBSchema(BaseClass):
    """Таблица связи баз данных и имен схем."""

    base = models.ForeignKey(DimDB, on_delete=models.PROTECT)
    schema = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.base}-{self.schema}'

    class Meta:
        db_table = f'{db_schema}\".\"link_base_schemas'
        unique_together = [['base', 'schema', ]]
        verbose_name = '05 Словарь схем баз данных.'
        verbose_name_plural = '05 Словарь схем баз данных.'


class DimDBTableType(BaseClass):
    """Справочник типов данных."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_table_type'
        unique_together = [['name', ]]
        verbose_name = '06 Словарь типов таблиц.'
        verbose_name_plural = '06 Словарь типов таблиц.'


class DimColumnName(BaseClass):
    """Список имен столбцов"""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"dim_column_name'
        unique_together = [['name', ]]
        verbose_name = '08 Словарь имен столбцов.'
        verbose_name_plural = '08 Словарь имен столбцов.'


class LinkDBTable(BaseClass):
    """Связи схем схем, типов таблиц и таблиц."""

    schema = models.ForeignKey(LinkDBSchema, on_delete=models.PROTECT)
    is_metadata = models.BooleanField(default=True, verbose_name='метаданные')
    type = models.ForeignKey(DimDBTableType, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.schema}-{self.type}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_tables'
        unique_together = [['schema', 'type', 'name', ]]
        verbose_name = '10 Связи схем и таблиц.'
        verbose_name_plural = '10 Связи схем и таблиц'


class LinkDBTableName(BaseClass):
    """
    Связи таблиц и их синонимов.
    """

    table = models.ForeignKey(LinkDBTable, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.table}-{self.name}'

    class Meta:
        unique_together = [['table', 'name', ]]
        db_table = f'{db_schema}\".\"link_tables_name'
        verbose_name = '14 Альтернативное название таблицы.'
        verbose_name_plural = '14 Альтернативные названия таблиц.'


class LinkColumn(BaseClass):
    """Связи таблиц типов данных и столбцов."""

    table = models.ForeignKey(LinkDBTable, on_delete=models.PROTECT, )
    date_create = models.DateTimeField(default=datetime.datetime.now)
    type = models.CharField(max_length=255, null=True, )
    columns = models.CharField(max_length=255, )
    is_null = models.BooleanField(blank=True, null=True, db_default=True, )
    is_key = models.BooleanField(db_default=False, )
    unique_together = models.IntegerField(blank=True, null=True, )
    default = models.TextField(blank=True, null=True, )
    description = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.table}-{self.columns}'

    class Meta:
        db_table = f'{db_schema}\".\"link_columns'
        unique_together = [['table', 'columns', ]]
        verbose_name = '11 Столбец.'
        verbose_name_plural = '11 Столбцы.'


class DimTypeLink(BaseClass):
    name = models.CharField(max_length=255, )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_type_link'
        unique_together = [['name', ]]
        verbose_name = '12 Справочник типов связей.'
        verbose_name_plural = '12 Справочник типов связей.'


class LinkColumnColumn(BaseClass):
    """Связи столбцов между собой."""

    type = models.ForeignKey(DimTypeLink, on_delete=models.PROTECT, )
    main = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, related_name='main')
    sub = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, related_name='sub', blank=True, null=True, )

    def __str__(self):
        return f'{self.main}-{self.sub}'

    class Meta:
        db_table = f'{db_schema}\".\"link_columns_columns'
        unique_together = [['main', 'sub', 'type', ]]
        verbose_name = '13 Связи столбцов.'
        verbose_name_plural = '13 Связи столбцов.'


class LinkColumnName(BaseClass):
    """синонимы названий столбцов."""

    column = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, )
    name = models.ForeignKey(DimColumnName, on_delete=models.PROTECT, )

    def __str__(self):
        return f'{self.column}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_columns_name'
        unique_together = [['column', 'name', ]]
        verbose_name = '14 Связь столбцов и имен столбцов.'
        verbose_name_plural = '14 Связь столбцов и имен столбцов.'


class LinkColumnStage(BaseClass):
    """Связи столбцов и стендов разработки."""

    stage = models.ForeignKey(DimStage, on_delete=models.PROTECT, )
    column = models.ForeignKey(LinkColumn, on_delete=models.PROTECT, )

    def __str__(self):
        return f'{self.stage}-{self.column}'

    class Meta:
        db_table = f'{db_schema}\".\"link_columns_stage'
        unique_together = [['stage', 'column', ]]
        verbose_name = '11 Связь столбца на стенде.'
        verbose_name_plural = '11 Связь столбца на стенде.'
