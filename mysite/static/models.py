from django.db import models
from django.urls import reverse


"""Конфликт текущих моделей с базовой. пришлось дублировать код"""


# class BasesClass(models.Model):
#     """Созданы базовые поля, важные для всех таблиц"""
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
#     hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
#     hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
#     is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    base = models.ForeignKey('BaseGroup', on_delete=models.PROTECT, blank=True, null=True, db_comment='Имя базы')
    host_name = models.CharField(max_length=255, blank=True, null=True, db_comment='Имя хоста')
    host_db = models.CharField(max_length=255, blank=True, null=True, db_comment='Имя хоста')
    version = models.CharField(max_length=255, blank=True, null=True, db_comment='Версия базы данных')
    type = models.ForeignKey('StageType', on_delete=models.PROTECT, blank=True, null=True, db_comment='Имя слоя')

    def __str__(self):
        return self.host_name

    def get_absolute_url(self):
        return reverse('stage_id', kwargs={"stage_id": self.pk})

    class Meta:
        db_table = 'name_base'
        db_table_comment = 'Список стендов данных.'
        verbose_name = '01 Base'
        verbose_name_plural = '01 Base'
        ordering = ['base', 'type']
        unique_together = [['base', 'type']]


class BaseGroup(models.Model):  # хотел назвать Base, но имя зарезервировано
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    table_catalog = models.CharField(max_length=150, db_comment='Имя базы данных')

    def __str__(self):
        return self.table_catalog

    def get_absolute_url(self):
        return reverse('base_id', kwargs={'base_id': self.pk})

    class Meta:
        db_table = 'name_base_group'
        db_table_comment = "Список баз данных."
        verbose_name = '02 BaseGroup'
        verbose_name_plural = '02 BaseGroup'
        ordering = ['table_catalog', ]


class Schema(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    base = models.ForeignKey('BaseGroup', on_delete=models.PROTECT, blank=True, null=True, db_comment='Имя базы')
    table_schema = models.CharField(max_length=150, db_comment='Имя схемы')
    comment = models.CharField(max_length=255, blank=True, null=True, db_comment='Комментарии к схеме базы данных')

    def __str__(self):
        return self.table_schema

    def get_absolute_url(self):
        return reverse('schema_id', kwargs={"schema_id": self.pk})

    class Meta:
        db_table_comment = "Список схем в базе данных."
        db_table = 'name_schema'
        verbose_name = '03 Schema'
        verbose_name_plural = '03 Schema'
        ordering = ['base', 'table_schema', ]
        unique_together = [['base', 'table_schema']]


class Table(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='Запись активна', db_comment='Админ поле. Актуально')
    is_metadata = models.BooleanField(default=False, verbose_name='Таблица метаданных', db_comment='Таблица метаданных')
    schema = models.ForeignKey('Schema', on_delete=models.PROTECT, blank=True, null=True, db_comment='Имя схемы')
    table_name = models.CharField(max_length=150, db_comment='Имя таблицы')
    table_ru = models.CharField(max_length=150, db_comment='Имя таблицы на русском языке')
    table_com = models.TextField(blank=True, null=True, db_comment='Комментарии таблицы базы данных оригинальное')


    def __str__(self):
        return self.table_name

    def get_absolute_url(self):
        return reverse('table_id', kwargs={"table_id": self.pk})

    class Meta:
        db_table = 'name_table'
        db_table_comment = "Список таблиц в базе данных."
        verbose_name = '04 Table'
        verbose_name_plural = '04 Table'
        ordering = ['schema', 'table_name', ]
        unique_together = [['schema', 'table_name']]


class Column(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    table = models.ForeignKey('Table', on_delete=models.PROTECT, blank=True, null=True, db_comment='Имя таблицы')
    date_create = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='Дата создания',
                                       db_comment='Дата создания')
    column_name = models.CharField(max_length=150, db_comment='Имя столбца')
    column_default = models.TextField(blank=True, null=True, db_comment='Значение по умолчанию')
    is_nullable = models.CharField(max_length=255, blank=True, null=True, db_comment='Допустимость NULL')
    data_type = models.CharField(max_length=255, blank=True, null=True, db_comment='Тип столбца')
    is_auto = models.CharField(max_length=255, blank=True, null=True, db_comment='Автоматическое поле')
    column_com = models.TextField(blank=True, null=True, db_comment='Комментарии таблицы базы данных')

    def __str__(self):
        return self.column_name

    def get_absolute_url(self):
        return reverse('column_id', kwargs={"column_id": self.pk})

    class Meta:
        db_table = 'name_column'
        db_table_comment = "Список столбцов в базе данных."
        verbose_name = '05 Column'
        verbose_name_plural = '05 Column'
        ordering = ['column_name', 'table', ]
        unique_together = [['table', 'column_name']]


class StageType(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    name = models.CharField(max_length=20, blank=True, null=True, db_comment='Слой базы данных', unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stage_type_id', kwargs={"stage_type_id": self.pk})

    class Meta:
        db_table = 'name_stage_type'
        db_table_comment = "Список стендов данных."
        verbose_name = '07 Stage'
        verbose_name_plural = '07 Stage'
        ordering = ['pk', ]


class StageColumn(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    stage = models.ForeignKey('Base', on_delete=models.PROTECT, blank=True, null=True, db_comment='Стенд')
    column = models.ForeignKey('Column', on_delete=models.PROTECT, blank=True, null=True, db_comment='Колонка')

    def __str__(self):
        return str(self.stage)

    def get_absolute_url(self):
        return reverse('hash_address_id', kwargs={"hash_address_id": self.pk})

    class Meta:
        db_table = 'link_stage_column'
        db_table_comment = "Связь столбец-схема данных"
        verbose_name = 'L-01 StageColumn'
        verbose_name_plural = 'L-01 StageColumn'
        ordering = ['stage', 'column', ]
        unique_together = [['stage', 'column']]


class ColumnColumn(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    main = models.ForeignKey('Column', related_name='main', db_comment='main колонка',
                             on_delete=models.PROTECT, blank=True, null=True)
    sub = models.ForeignKey('Column', related_name='sub', db_comment='sub колонка',
                            on_delete=models.PROTECT, blank=True, null=True)
    TYPE_LIST = [
        ('link', 'Ссылка'),
        ('update', 'Обновление'),
        ('link_cond', 'Ссылка условная'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_LIST, default='link',
                            db_comment='Тип связи')
    update = models.ForeignKey('Update', on_delete=models.CASCADE, blank=True, null=True,
                               db_comment='Расписание обновлений')  # Расписание обновлений

    def __str__(self):
        return str(self.main)

    def get_absolute_url(self):
        return reverse('hash_address_id', kwargs={"hash_address_id": self.pk})

    class Meta:
        db_table = 'link_column_column'
        db_table_comment = "Связь столбец-столбец"
        verbose_name = 'L-02 LinkColumn'
        verbose_name_plural = 'L-02 LinkColumn'
        unique_together = [['main', 'sub', 'type']]


# ----start=Update----start=Update----start=Update----start=Update----start=Update----start=Update----start=Update----
class UpdateMethod(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    method = models.CharField(max_length=255, blank=True, null=True, db_comment='Тип обновления')

    def __str__(self):
        return self.method

    def get_absolute_url(self):
        return reverse('update_method_id', kwargs={"update_method_id": self.pk})

    class Meta:
        db_table = 'link_update_method'
        db_table_comment = "Способ обновления."
        verbose_name = '06 method update'
        verbose_name_plural = '06 method update'


class Update(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    name = models.CharField(max_length=255, blank=True, null=True, db_comment='Название обновления')
    description = models.TextField(blank=True, null=True, db_comment='Описание обновления')
    type = models.CharField(max_length=255, blank=True, null=True, db_comment='Тип обновления')
    schedule = models.CharField(max_length=50, blank=True, null=True, db_comment='Расписание обновления')
    method = models.ForeignKey('UpdateMethod', on_delete=models.PROTECT, blank=True, null=True, db_comment='Метод')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('update_id', kwargs={"update_id": self.pk})

    class Meta:
        db_table = 'link_update'
        db_table_comment = "Расписание обновлений."
        verbose_name = '06 update'
        verbose_name_plural = '06 update'


# ----stop=Update----stop=Update----stop=Update----stop=Update----stop=Update----stop=Update----stop=Update----
class Function(models.Model):
    """Функции базы данных"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    schema = models.ForeignKey('Schema', on_delete=models.PROTECT, db_comment='Имя схема данных')
    name_fun = models.CharField(max_length=255, db_comment='Название функции')
    code = models.TextField(blank=True, null=True, db_comment='Код')
    function_com = models.TextField(blank=True, null=True, db_comment='Комментарии к функции из базы данных')

    def __str__(self):
        return self.name_fun

    def get_absolute_url(self):
        return reverse('function_id', kwargs={'function_id': self.pk})

    class Meta:
        db_table = 'name_function'
        db_table_comment = "Список функций базы данных"
        verbose_name = '10 Функции БД'
        verbose_name_plural = '10 Функции БД'
        ordering = ['schema', 'name_fun', ]
        unique_together = [['schema', 'name_fun']]


class StageFunction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    stage = models.ForeignKey('Base', on_delete=models.PROTECT, blank=True, null=True, db_comment='Стенд')
    function = models.ForeignKey('Function', on_delete=models.PROTECT, blank=True, null=True, db_comment='функция')

    def __str__(self):
        return str(self.stage)

    def get_absolute_url(self):
        return reverse('stage_function_id', kwargs={"stage_function_id": self.pk})

    class Meta:
        db_table = 'link_stage_function'
        db_table_comment = "Связь база-функция"
        verbose_name = 'L-03 LinkFunction'
        verbose_name_plural = 'L-03 LinkFunction'
        unique_together = [['stage', 'function', ]]


class Service(models.Model):  # хотел назвать Base, но имя зарезервировано
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    service = models.CharField(max_length=150, db_comment='Имя базы группы')

    def __str__(self):
        return self.service

    def get_absolute_url(self):
        return reverse('service_id', kwargs={'service_id': self.pk})

    class Meta:
        db_table = 'name_service'
        db_table_comment = "Список сервисов."
        verbose_name = '08 service'
        verbose_name_plural = '08 service'
        ordering = ['service', ]


class ServiceTable(models.Model):  # хотел назвать Base, но имя зарезервировано
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания', db_comment='Админ поле. Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения', db_comment='Админ поле. Обновлено')
    hash_address = models.CharField(max_length=64, unique=True, db_comment='адрес данных по хеш')
    hash_data = models.CharField(max_length=64, unique=True, db_comment='хеш сумма части строки')
    is_active = models.BooleanField(default=True, verbose_name='запись активна', db_comment='Админ поле. Актуально')
    service = models.ForeignKey('Service', on_delete=models.PROTECT, blank=True, null=True, db_comment='Сервис')
    table = models.ForeignKey('Table', on_delete=models.PROTECT, blank=True, null=True, db_comment='Таблица')

    def __str__(self):
        return str(self.service) + '-' + str(self.table)

    def get_absolute_url(self):
        return reverse('service_table_id', kwargs={'service_table_id': self.pk})

    class Meta:
        db_table = 'name_service_table'
        db_table_comment = "Группы таблиц - сервисы."
        verbose_name = '09 Service Table'
        verbose_name_plural = '09 Service Table'
        ordering = ['service', 'table', ]
        unique_together = [['service', 'table', ]]
