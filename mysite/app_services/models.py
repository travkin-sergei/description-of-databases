# app_services/models.py
from django.db import models

from app_auth.models import MyProfile
from app_url.models import DimUrl
from app_dbm.models import LinkTable, DimStage
from app_doc.models import DimDoc
from _common.models import BaseClass

from .apps import db_schema


class DimServicesTypes(BaseClass):
    """Типы сервисов"""

    name = models.CharField(max_length=255)

    class Meta:
        db_table = f'{db_schema}"."dim_services_type'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '02 Типы сервисов.'
        verbose_name_plural = '02 Типы сервисов.'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class DimServices(BaseClass):
    """Список сервисов."""

    alias = models.CharField(max_length=255)
    type = models.ForeignKey(DimServicesTypes, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)

    @property
    def all_names(self):
        """Возвращает все названия (alias + синонимы)"""
        names = [self.alias]
        names.extend([ns.name for ns in self.dimservicesname_set.all()])
        return names

    def __str__(self):
        return f'{self.alias}-{self.type}'

    class Meta:
        db_table = f'{db_schema}"."dim_services'
        unique_together = [
            ['alias', 'type', ]
        ]
        verbose_name = '07 Список сервисов.'
        verbose_name_plural = '07 Список сервисов.'
        ordering = ['alias']


class LinkServicesServices(BaseClass):
    """Связи сервисов между собой."""

    main = models.ForeignKey(DimServices, on_delete=models.PROTECT, related_name='my_main')
    sub = models.ForeignKey(DimServices, on_delete=models.PROTECT, related_name='my_sub')

    def __str__(self):
        return f'{self.main}-{self.sub}'

    class Meta:
        db_table = f'{db_schema}"."link_services_services'
        unique_together = [
            ['main', 'sub', ]
        ]
        verbose_name = '08 Группировки сервисов.'
        verbose_name_plural = '08 Группировки сервисов.'


class DimServicesNameType(BaseClass):
    """Тип имени таблицы"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = f'{db_schema}"."dim_services_name_type'
        unique_together = [['name', ]]
        verbose_name = '08 Словарь типов наименований.'
        verbose_name_plural = '08 Словарь типов наименований.'


class DimServicesName(BaseClass):
    """Синонимы для сервиса."""

    alias = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    type = models.ForeignKey(DimServicesNameType, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.alias}-{self.name}'

    class Meta:
        db_table = f'{db_schema}"."dim_services_name'
        unique_together = [
            ['alias', 'name', ]
        ]
        verbose_name = '03 Синонимы сервисов.'
        verbose_name_plural = '03 Синонимы сервисов.'


class DimRoles(BaseClass):
    """Справочник ролей ответственных."""

    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}"."dim_roles'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '001 Роли в сервисе.'
        verbose_name_plural = '001 Роли в сервисах.'


class LinkResponsiblePerson(BaseClass):
    """Связи сервисов и профилей пользователей с указанием ролевых моделей."""

    service = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    role = models.ForeignKey(DimRoles, on_delete=models.PROTECT)
    name = models.ForeignKey(MyProfile, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.service}-{self.role}-{self.name}'

    class Meta:
        db_table = f'{db_schema}"."link_responsible_person'
        unique_together = [
            ['service', 'role', 'name', ]
        ]
        verbose_name = '04 Ответственные за сервис.'
        verbose_name_plural = '04 Ответственные за сервис.'


class LinkServicesTable(BaseClass):
    """Список таблиц сервиса."""

    service = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    table = models.ForeignKey(LinkTable, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.service}-{self.table}'

    class Meta:
        db_table = f'{db_schema}"."link_service_table'
        unique_together = [
            ['service', 'table', ]
        ]
        verbose_name = '09 Таблицы сервиса.'
        verbose_name_plural = '09 Таблицы сервиса.'


class DimTechStack(BaseClass):
    name = models.CharField(max_length=255)  # Исправлено: добавлен max_length
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}"."link_tech_stack'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '06 Технология.'
        verbose_name_plural = '06 Технологии.'


class LinksUrlService(BaseClass):
    """Отнесение URL к сервису."""

    url = models.ForeignKey(DimUrl, on_delete=models.PROTECT, blank=True, null=True)
    service = models.ForeignKey(DimServices, on_delete=models.PROTECT, blank=True, null=True)
    link_name = models.CharField(max_length=255)
    stage = models.ForeignKey(DimStage, on_delete=models.PROTECT, blank=True, null=True)
    stack = models.ForeignKey(DimTechStack, on_delete=models.PROTECT, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.url}'

    class Meta:
        db_table = f'{db_schema}"."link_url_service'
        unique_together = [
            ['url', ]
        ]
        verbose_name = '09 ссылки.'
        verbose_name_plural = '09 ссылки.'
        ordering = ['url']


class LinkDoc(BaseClass):
    """Связь сервиса и документа."""

    services = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    doc = models.ForeignKey(DimDoc, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.services}-{self.doc}"

    class Meta:
        db_table = f'{db_schema}"."link_doc'  # Исправлено: изменено имя таблицы с dim_schedule на link_doc
        unique_together = [['services', 'doc', ]]
        verbose_name = '011 Сервис и документ'
        verbose_name_plural = '011 Сервисы и документы'