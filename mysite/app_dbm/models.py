# app_dbm/models.py
import datetime
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from _common.models import BaseClass, hash_calculate
from .apps import db_schema


class TotalData(BaseClass):
    """Содержит полные загружаемые извне данные."""

    hash_address = models.CharField(max_length=64, primary_key=True, verbose_name='Хеш сумма')
    # -----
    stand = models.CharField(max_length=255, blank=True, null=True, verbose_name='стенд')
    table_type = models.CharField(max_length=255, blank=True, null=True, verbose_name='тип таблицы')
    group_catalog = models.CharField(max_length=255, blank=True, null=True, verbose_name='группа базы данных')
    table_catalog = models.CharField(max_length=255, blank=True, null=True, verbose_name='имя базы данных')
    table_schema = models.CharField(max_length=255, blank=True, null=True, verbose_name='схема таблицы')
    table_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='имя таблицы')
    table_comment = models.CharField(max_length=255, blank=True, null=True, verbose_name='комментарий таблицы')
    column_number = models.CharField(max_length=255, blank=True, null=True, verbose_name='номер столбца')
    column_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='имя столбца')
    column_comment = models.CharField(max_length=255, blank=True, null=True, verbose_name='комментарий столбца')
    data_type = models.CharField(max_length=255, blank=True, null=True, verbose_name='тип данных')
    is_nullable = models.CharField(max_length=255, blank=True, null=True, verbose_name='поле пустое')
    is_auto = models.CharField(max_length=255, blank=True, null=True, verbose_name='автоматическое')
    column_info = models.JSONField(blank=True, null=True, verbose_name='дополнительная информация о данных')

    class Meta:
        db_table = f'{db_schema}"."set_total_data'  # Убедитесь, что db_schema определен
        verbose_name = '00 Полная информация о данных.'
        verbose_name_plural = '00 Полная информация о данных.'

    def save(self, *args, **kwargs):
        """
        Переопределяем save для:
        1. Генерации хэша при создании новой записи
        2. Сохранения created_at только при создании
        3. Обновления updated_at при каждом сохранении
        """
        # Определяем, создается ли новая запись
        is_new = self._state.adding  # True если объект еще не сохранен в БД

        # Если это новая запись и hash_address не задан
        if is_new and not self.hash_address:
            self.hash_address = self.calculate_hash()

        # Если это обновление существующей записи
        if not is_new:
            # Обновляем updated_at вручную, если auto_now недостаточно
            self.updated_at = timezone.now().date()

        # Вызываем родительский метод save
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_with_hash(cls, **kwargs):
        # Формируем ключи хеширования по тем же полям
        hash_fields = [
            kwargs.get('stand'),
            kwargs.get('table_catalog'),
            kwargs.get('table_schema'),
            kwargs.get('table_type'),
            kwargs.get('table_name'),
            kwargs.get('column_name'),
        ]
        hash_address = hash_calculate(hash_fields)

        # Используем update_or_create — он ищет по hash_address, обновляет по defaults
        obj, created = cls.objects.update_or_create(
            hash_address=hash_address,
            defaults=kwargs
        )
        return obj, created

    def update_timestamp(self):
        """Ручное обновление updated_at."""
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])


# 01 Словарь слоев.
class DimStage(BaseClass):
    """Справочник стендов разработки."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_stage'
        unique_together = [["name"]]
        verbose_name = '01 Словарь слоев.'
        verbose_name_plural = '01 Словарь слоев.'


# 02 Словарь баз данных.
class DimDB(BaseClass):
    """ Справочник баз данных."""

    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}"."dim_db'
        unique_together = [['name', ]]
        verbose_name = '02 Словарь баз данных.'
        verbose_name_plural = '02 Словарь баз данных.'
        ordering = ['name']


# 03 Базы данных.
class LinkDB(BaseClass):
    """ Справочник баз данных."""

    base = models.ForeignKey(DimDB, on_delete=models.CASCADE)
    version = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    stage = models.ForeignKey(DimStage, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.host})"

    class Meta:
        db_table = f'{db_schema}"."link_db'
        unique_together = [['name', 'host', 'port', ]]
        verbose_name = '03 Базы данных.'
        verbose_name_plural = '03 Базы данных.'


# 04 Схема
class LinkSchema(BaseClass):
    """Таблица связи баз данных и имен схем."""

    base = models.ForeignKey(DimDB, on_delete=models.CASCADE)
    schema = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.base}-{self.schema}'

    class Meta:
        db_table = f'{db_schema}"."link_schemas'
        unique_together = [['base', 'schema', ]]
        verbose_name = '04 Схема.'
        verbose_name_plural = '04 Схемы.'


# 05 Словарь тип таблицы.
class DimTableType(BaseClass):
    """Справочник типов данных."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_table_type'
        unique_together = [['name', ]]
        verbose_name = '05 Словарь тип таблицы.'
        verbose_name_plural = '05 Словарь типы таблиц.'


# 07 Словарь имен столбцов.
class DimColumnName(BaseClass):
    """Список имен столбцов"""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_column_name'
        unique_together = [['name', ]]
        verbose_name = '07 Словарь имен столбцов.'
        verbose_name_plural = '07 Словарь имен столбцов.'
        ordering = ['name']


# 08 Словарь типов наименований.
class DimTableNameType(BaseClass):
    """Тип имени таблицы"""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_table_name_type'
        unique_together = [['name', ]]
        verbose_name = '08 Словарь типов наименований.'
        verbose_name_plural = '08 Словарь типов наименований.'
        ordering = ['name']


# 09 Таблица.
class LinkTable(BaseClass):
    """Связи схем схем, типов таблиц и таблиц."""

    schema = models.ForeignKey(LinkSchema, on_delete=models.CASCADE)
    is_metadata = models.BooleanField(default=True, verbose_name='метаданные')
    type = models.ForeignKey(DimTableType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.schema}-{self.type}-{self.name}'

    class Meta:
        db_table = f'{db_schema}"."link_tables'
        unique_together = [['schema', 'type', 'name', ]]
        verbose_name = '09 Таблица.'
        verbose_name_plural = '09 Таблицы'
        ordering = ['schema']


# 10 Альтернативное название таблицы.
class LinkTableName(BaseClass):
    """Связи таблиц и их синонимов."""

    table = models.ForeignKey(LinkTable, on_delete=models.CASCADE, )
    type = models.ForeignKey(DimTableNameType, on_delete=models.CASCADE, )
    name = models.CharField(max_length=255)
    is_publish = models.BooleanField(null=True, blank=True, default=False, verbose_name='Указать как основное?')

    def __str__(self):
        return f'{self.table}-{self.name}'

    def save(self, *args, **kwargs):
        # Если is_publish True, сбрасываем у других записей для той же таблицы
        if self.is_publish:
            with transaction.atomic():
                # Сбросить is_publish у других записей той же таблицы
                LinkTableName.objects.filter(
                    table=self.table
                    , is_publish=True
                ).exclude(
                    pk=self.pk
                ).update(
                    is_publish=False
                )
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    class Meta:
        unique_together = [['table', 'name']]
        db_table = f'{db_schema}"."link_tables_name'
        verbose_name = '10 Альтернативное название таблицы.'
        verbose_name_plural = '10 Альтернативные названия таблиц.'
        constraints = [
            models.UniqueConstraint(
                fields=['table'],
                condition=Q(is_publish=True),
                name='unique_publish_per_table'
            )
        ]
        ordering = ['name']


# 11 Столбец.
class LinkColumn(BaseClass):
    """Связи таблиц типов данных и столбцов."""

    table = models.ForeignKey(LinkTable, on_delete=models.CASCADE)
    date_create = models.DateTimeField(default=datetime.datetime.now)
    type = models.CharField(max_length=255, null=True)
    columns = models.CharField(max_length=255)
    is_null = models.BooleanField(blank=True, null=True, db_default=True)
    is_key = models.BooleanField(db_default=False)
    unique_together = models.IntegerField(blank=True, null=True)
    default = models.TextField(blank=True, null=True)
    description = models.JSONField(blank=True, null=True)
    stage = models.JSONField(
        blank=True, null=True,
        verbose_name="Доп. информация о слое",
        help_text='{"1": "Sand","2": "DEV", "3": "TEST","4": "PreProd", "5": "Prod",}'
    )

    def __str__(self):
        try:
            return f"{self.table.schema.base.name}.{self.table.schema.schema}.{self.table.name}.{self.columns}"
        except Exception:
            return f"LinkColumn #{self.pk}"

    class Meta:
        db_table = f'"{db_schema}"."link_columns"'
        unique_together = [['table', 'columns']]
        verbose_name = '11 Столбец.'
        verbose_name_plural = '11 Столбцы.'
        ordering = ['columns']


# 12 Справочник типов связей.
class DimTypeLink(BaseClass):
    name = models.CharField(max_length=255, )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}"."dim_type_link'
        unique_together = [['name', ]]
        verbose_name = '12 Справочник типов связей.'
        verbose_name_plural = '12 Справочник типов связей.'
        ordering = ['name']


# 13 Связи столбцов.
class LinkColumnColumn(BaseClass):
    """Связи столбцов между собой."""

    type = models.ForeignKey(DimTypeLink, on_delete=models.CASCADE)
    main = models.ForeignKey(LinkColumn, on_delete=models.CASCADE, related_name='main')
    sub = models.ForeignKey(LinkColumn, on_delete=models.CASCADE, related_name='sub', blank=True, null=True)

    def __str__(self):
        return f'{self.main}-{self.sub}'

    class Meta:
        db_table = f'{db_schema}"."link_columns_columns'
        unique_together = [['main', 'sub', 'type']]
        verbose_name = '13 Связи столбцов.'
        verbose_name_plural = '13 Связи столбцов.'
        ordering = ['main']
        constraints = [
            models.UniqueConstraint(
                fields=['main', 'sub', 'type'],
                name='unique_columns_relation'
            ),
            models.UniqueConstraint(
                fields=['main'],
                condition=Q(sub__isnull=True),
                name='unique_main_only'
            ),
        ]
        indexes = [
            models.Index(fields=['main']),
            models.Index(fields=['sub']),
            models.Index(fields=['type']),
        ]


# 14 Связь столбцов и имен столбцов.
class LinkColumnName(BaseClass):
    """синонимы названий столбцов."""

    column = models.ForeignKey(LinkColumn, on_delete=models.CASCADE, )
    name = models.ForeignKey(DimColumnName, on_delete=models.CASCADE, )

    def __str__(self):
        return f'{self.column}-{self.name}'

    class Meta:
        db_table = f'{db_schema}"."link_columns_name'
        unique_together = [['column', 'name', ]]
        verbose_name = '14 Связь столбцов и имен столбцов.'
        verbose_name_plural = '14 Связь столбцов и имен столбцов.'
        ordering = ['name']
