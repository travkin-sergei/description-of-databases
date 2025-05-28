"""
1) Конфликт текущих моделей с базовой. пришлось дублировать код
2) Пришлось понизить версию django c 5 до 4.1 из-за версии базы данных. 4.2 и выше требует 12 версию Postgres
   поэтому пришлось закомментировать комментарии к столбцам и таблицам базы данных
"""

import hashlib

from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse

db_schema = 'my_dba'

class BasesClass(models.Model):
    """Созданы базовые поля, важные для всех таблиц"""
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='дата создания')  # , db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='дата изменения')  # , db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True)  # , db_comment='адрес данных по хеш')
    is_active = models.BooleanField(default=True,
                                    verbose_name='запись активна')  # , db_comment='Админ поле. Актуально')

    def hash_sum_256(self, args):
        list_str = [str(i) for i in args]
        list_union = '+'.join(list_str)
        return hashlib.sha256(list_union.encode()).hexdigest()

    def get_hash_fields(self):
        # переопределить в каждой модели
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """для атрибута version"""
        pre_save.send(sender=self.__class__, instance=self, request=kwargs.get('request'))
        self.hash_address = self.hash_sum_256(self.get_hash_fields())  # recalculate hash on every save
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Base(BasesClass):
    base = models.ForeignKey('BaseGroup', on_delete=models.PROTECT, blank=True, null=True)
    host_name = models.CharField(max_length=255, blank=True, null=True)
    host_db = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey('StageType', on_delete=models.PROTECT, blank=True, null=True)

    def get_hash_fields(self):
        return [self.base, self.type, ]

    def __str__(self):
        return self.host_db

    class Meta:
        db_table = f'{db_schema}\".\"name_base'
        # db_table_comment = 'Список стендов данных.'
        verbose_name = '01 Base'
        verbose_name_plural = '01 Base'
        ordering = ['base', 'type']
        unique_together = [['base', 'type']]


class BaseGroup(BasesClass):  # хотел назвать Base, но имя зарезервировано

    table_catalog = models.CharField(max_length=150)

    def get_hash_fields(self):
        return [
            self.table_catalog,
        ]

    def __str__(self):
        return self.table_catalog

    class Meta:
        db_table = f'{db_schema}\".\"name_base_group'
        # db_table_comment = "Список баз данных."
        verbose_name = '02 BaseGroup'
        verbose_name_plural = '02 BaseGroup'
        ordering = ['table_catalog', ]


class Schema(BasesClass):
    base = models.ForeignKey('BaseGroup', on_delete=models.PROTECT, blank=True, null=True)
    table_schema = models.CharField(max_length=150)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def get_hash_fields(self):
        return [
            self.base.table_catalog,
            self.table_schema
        ]

    def __str__(self):
        return self.table_schema

    class Meta:
        db_table = f'{db_schema}\".\"name_schema'
        verbose_name = '03 Schema'
        verbose_name_plural = '03 Schema'
        ordering = ['base', 'table_schema', ]
        unique_together = [['base', 'table_schema']]


class Table(BasesClass):
    """
    Таблицы базы данных
    """
    TYPE_LIST = [
        ('tabl', 'Таблица'),
        ('ext_tabl', 'Внешняя таблица'),
        ('view', 'Представление'),
    ]

    is_metadata = models.BooleanField(default=False, verbose_name='Таблица метаданных')
    type = models.CharField(max_length=10, choices=TYPE_LIST, default='tabl', verbose_name='Тип таблицы')
    schema = models.ForeignKey('Schema', on_delete=models.PROTECT, blank=True, null=True)
    table_name = models.CharField(max_length=150, verbose_name='название в БД')
    table_ru = models.TextField(verbose_name='наименование')
    table_com = models.TextField(blank=True, null=True, verbose_name='комментарий')

    def get_hash_fields(self):
        return [
            self.schema.base.table_catalog,
            self.schema.table_schema,
            self.table_name
        ]

    def __str__(self):
        return self.table_name

    class Meta:
        db_table = f'{db_schema}\".\"name_table'
        # db_table_comment = "Список таблиц в базе данных."
        verbose_name = '04 Table'
        verbose_name_plural = '04 Table'
        ordering = ['schema', 'table_name', 'id']
        unique_together = [['schema', 'type', 'table_name']]


class ColumnMDType(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='дата создания')  # , db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='дата изменения')  # , db_comment='Админ поле. Обновлено')
    is_active = models.BooleanField(default=True,
                                    verbose_name='запись активна')  # , db_comment='Админ поле. Актуально')
    md_type = models.CharField(max_length=150, unique=True)  # , db_comment='Описание')

    def get_hash_fields(self):
        return ['md_type', ]

    def __str__(self):
        return self.md_type

    class Meta:
        db_table = f'{db_schema}\".\"name_column_mdt'
        # db_table_comment = "Группы таблиц - сервисы."
        verbose_name = '11 meta data Type'
        verbose_name_plural = '11 meta data Type'
        ordering = ['md_type', ]


class Column(BasesClass):
    table = models.ForeignKey('Table', on_delete=models.PROTECT, blank=True, null=True)
    date_create = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='Дата создания')
    column_name = models.TextField()
    column_default = models.TextField(blank=True, null=True)
    is_nullable = models.CharField(blank=True, null=True, max_length=255)
    data_type = models.CharField(blank=True, null=True, max_length=255)
    is_auto = models.CharField(blank=True, null=True, max_length=255)
    column_com = models.TextField(blank=True, null=True)
    md_type = models.ForeignKey('ColumnMDType', on_delete=models.PROTECT, blank=True, null=True)

    def get_hash_fields(self):
        return [
            self.table.schema.base.table_catalog,
            self.table.schema.table_schema,
            self.table.table_name,
            self.column_name
        ]

    def __str__(self):
        return self.column_name

    class Meta:
        db_table = f'{db_schema}\".\"name_column'
        # db_table_comment = "Список столбцов в базе данных."
        verbose_name = '05 Column'
        verbose_name_plural = '05 Column'
        ordering = ['table', 'id', ]
        unique_together = [['table', 'column_name']]


class StageType(BasesClass):
    name = models.CharField(max_length=20, blank=True, null=True)  # , db_comment='Слой базы данных', unique=True)

    def get_hash_fields(self):
        return [self.name]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"name_stage_type'
        # db_table_comment = "Список стендов данных."
        verbose_name = '07 Stage'
        verbose_name_plural = '07 Stage'
        ordering = ['pk', ]


class StageColumn(BasesClass):
    stage = models.ForeignKey('Base', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='Стенд')
    column = models.ForeignKey('Column', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='Колонка')

    def get_hash_fields(self):
        return [self.stage, self.column]

    def __str__(self):
        return str(self.stage)

    class Meta:
        db_table = f'{db_schema}\".\"link_stage_column'
        # db_table_comment = "Связь столбец-схема данных"
        verbose_name = 'L-01 StageColumn'
        verbose_name_plural = 'L-01 StageColumn'
        ordering = ['stage', 'column', ]
        unique_together = [['stage', 'column']]


class ColumnColumn(BasesClass):
    main = models.ForeignKey('Column', related_name='main',
                             on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='main колонка',
    sub = models.ForeignKey('Column', related_name='sub',
                            on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='sub колонка',
    TYPE_LIST = [
        ('link', 'Ссылка'),
        ('update', 'Обновление'),
        ('link_cond', 'Ссылка условная'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_LIST, default='link', )
    # db_comment='Тип связи')
    update = models.ForeignKey('Update', on_delete=models.CASCADE, blank=True, null=True, )

    # db_comment='Расписание обновлений')  # Расписание обновлений
    def get_hash_fields(self):
        return [self.type, self.main, self.sub, self.update]

    def __str__(self):
        return str(self.main)

    class Meta:
        db_table = f'{db_schema}\".\"link_column_column'
        # db_table_comment = "Связь столбец-столбец"
        verbose_name = 'L-02 LinkColumn'
        verbose_name_plural = 'L-02 LinkColumn'
        unique_together = [['type', 'main', 'sub', 'update']]


# ----start=Update----start=Update----start=Update----start=Update----start=Update----start=Update----start=Update----
class UpdateMethod(BasesClass):
    method = models.CharField(max_length=255, blank=True, null=True)  # , db_comment='Тип обновления')

    def get_hash_fields(self):
        return [self.method, ]

    def __str__(self):
        return self.method

    class Meta:
        db_table = f'{db_schema}\".\"link_update_method'
        # db_table_comment = "Способ обновления."
        verbose_name = '06 method update'
        verbose_name_plural = '06 method update'


class Update(BasesClass):
    name = models.CharField(max_length=255, blank=True, null=True)  # , db_comment='Название обновления')
    description = models.TextField(blank=True, null=True)  # , db_comment='Описание обновления')
    type = models.CharField(max_length=255, blank=True, null=True)  # , db_comment='Тип обновления')
    schedule = models.CharField(max_length=50, blank=True, null=True)  # , db_comment='Расписание обновления')
    method = models.ForeignKey('UpdateMethod', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='Метод')
    link_code = models.URLField(blank=True, null=True)

    def get_hash_fields(self):
        return [self.name, self.type, self.method, ]

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}\".\"link_update'
        # db_table_comment = "Расписание обновлений."
        verbose_name = '06 update'
        verbose_name_plural = '06 update'


# ----stop=Update----stop=Update----stop=Update----stop=Update----stop=Update----stop=Update----stop=Update----
class Function(BasesClass):
    """Функции базы данных"""
    schema = models.ForeignKey('Schema', on_delete=models.PROTECT)  # , db_comment='Имя схема данных')
    name_fun = models.CharField(max_length=255)  # , db_comment='Название функции')
    code = models.TextField(blank=True, null=True)  # , db_comment='Код')
    function_com = models.TextField(blank=True, null=True)  # , db_comment='Комментарии к функции из базы данных')

    def get_hash_fields(self):
        return [self.schema, self.name_fun, ]

    def __str__(self):
        return self.name_fun

    class Meta:
        db_table = f'{db_schema}\".\"name_function'
        # db_table_comment = "Список функций базы данных"
        verbose_name = '10 Функции БД'
        verbose_name_plural = '10 Функции БД'
        ordering = ['schema', 'name_fun', ]
        unique_together = [['schema', 'name_fun']]


class StageFunction(BasesClass):
    stage = models.ForeignKey('Base', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='Стенд')
    function = models.ForeignKey('Function', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='функция')

    def get_hash_fields(self):
        return [self.stage, self.function, ]

    def __str__(self):
        return str(self.stage)

    class Meta:
        db_table = f'{db_schema}\".\"link_stage_function'
        # db_table_comment = "Связь база-функция"
        verbose_name = 'L-03 LinkFunction'
        verbose_name_plural = 'L-03 LinkFunction'
        unique_together = [['stage', 'function', ]]


class Service(BasesClass):  # хотел назвать Base, но имя зарезервировано
    service = models.TextField()  # db_comment='Имя базы группы')

    def get_hash_fields(self):
        return [self.service, ]

    def __str__(self):
        return self.service

    class Meta:
        db_table = f'{db_schema}\".\"name_service'
        # db_table_comment = "Список сервисов."
        verbose_name = '08 service'
        verbose_name_plural = '08 service'
        ordering = ['service', ]


class ServiceTable(BasesClass):  # хотел назвать Base, но имя зарезервировано
    service = models.ForeignKey('Service', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='Сервис')
    table = models.ForeignKey('Table', on_delete=models.PROTECT, blank=True, null=True)  # , db_comment='Таблица')

    def get_hash_fields(self):
        return [self.service, self.table, ]

    def __str__(self):
        return str(self.service) + '-' + str(self.table)

    class Meta:
        db_table = f'{db_schema}\".\"name_service_table'
        # db_table_comment = "Группы таблиц - сервисы."
        verbose_name = '09 Service Table'
        verbose_name_plural = '09 Service Table'
        ordering = ['service', 'table', ]
        unique_together = [['service', 'table', ]]
