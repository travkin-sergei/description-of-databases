import datetime

from django.db import models

db_schema = 'my_upload'


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


class ListRawData(BaseClass):
    """Таблица загруженных данных."""

    base_version = models.CharField(max_length=255)
    base_name = models.CharField(max_length=255)
    base_description = models.TextField(blank=True, null=True)
    base_alias = models.CharField(max_length=255, blank=True, null=True)
    base_host = models.CharField(max_length=255)
    base_port = models.CharField(max_length=255)

    schema = models.CharField(max_length=255)
    schema_description = models.TextField(blank=True, null=True)

    table_is_metadata = models.BooleanField(default=False)
    table_type = models.CharField()
    table_name = models.CharField(max_length=255)
    table_description = models.TextField(blank=True, null=True)

    column_date_create = models.DateTimeField(default=datetime.datetime.now)
    column_type = models.CharField(max_length=255, blank=True, null=True)
    column_columns = models.CharField(max_length=255, )
    column_is_null = models.BooleanField(blank=True, null=True, db_default=True, )
    column_is_key = models.BooleanField(db_default=False, )
    column_unique_together = models.IntegerField(blank=True, null=True, )
    column_default = models.TextField(blank=True, null=True, )
    column_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk}"

    class Meta:
        db_table = f'{db_schema}\".\"list_raw_data'
        unique_together = [['base_name', 'schema', 'table_type', 'table_name', 'column_columns']]
        verbose_name = '01 Список баз данных.'
        verbose_name_plural = '01 Список баз данных.'
