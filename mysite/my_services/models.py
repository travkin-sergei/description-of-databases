from my_dbm.models import (
    BaseClass,
    LinkDBTable,
    DimStage,
)
from my_auth.models import MyProfile
from django.db import models

db_schema = 'my_services'


class DimServicesTypes(BaseClass):
    """Типы сервисов"""

    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_services_type'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '02 Типы сервисов.'
        verbose_name_plural = '02 Типы сервисов.'


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
        db_table = f'{db_schema}\".\"dim_services'
        unique_together = [
            ['alias', 'type', ]
        ]
        verbose_name = '08 Список сервисов.'
        verbose_name_plural = '08 Список сервисов.'


class LinkServicesServices(BaseClass):
    """"""
    main = models.ForeignKey(DimServices, on_delete=models.PROTECT, related_name='my_main')
    sub = models.ForeignKey(DimServices, on_delete=models.PROTECT, related_name='my_sub')

    def __str__(self):
        return f'{self.main}-{self.sub}'

    class Meta:
        db_table = f'{db_schema}\".\"link_services_services'
        unique_together = [
            ['main', 'sub', ]
        ]
        verbose_name = '04 Группировки сервисов.'
        verbose_name_plural = '04 Группировки сервисов.'


class DimServicesName(BaseClass):
    """Синонимы для сервиса."""

    alias = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.alias}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"dim_services_name'
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
        db_table = f'{db_schema}\".\"dim_roles'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '01 Роли в сервисе.'
        verbose_name_plural = '01 Роли в сервисах.'


class LinkResponsiblePerson(BaseClass):
    service = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    role = models.ForeignKey(DimRoles, on_delete=models.PROTECT)
    name = models.ForeignKey(MyProfile, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.service}-{self.role}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_responsible_person'
        unique_together = [
            ['service', 'role', 'name', ]
        ]
        verbose_name = '04 Ответственные за сервис.'
        verbose_name_plural = '04 Ответственные за сервис.'


class LinkServicesTable(BaseClass):
    """Список таблиц сервиса."""

    service = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    table = models.ForeignKey(LinkDBTable, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.service}-{self.table}'

    class Meta:
        db_table = f'{db_schema}\".\"link_service_table'
        unique_together = [
            ['service', 'table', ]
        ]
        verbose_name = '05 Таблицы сервиса.'
        verbose_name_plural = '05 Таблицы сервиса.'


class DimTechStack(BaseClass):
    name = models.CharField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_tech_stack'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '06 Технология.'
        verbose_name_plural = '06 Технологии.'


class Swagger(BaseClass):
    """Swagger."""

    service = models.ForeignKey(DimServices, on_delete=models.PROTECT)
    stage = models.ForeignKey(DimStage, on_delete=models.PROTECT)
    swagger = models.URLField()

    def __str__(self):
        return f'{self.service}-{self.swagger}'

    class Meta:
        db_table = f'{db_schema}\".\"link_swagger'
        unique_together = [
            ['service', 'swagger', ]
        ]
        verbose_name = '07 swagger.'
        verbose_name_plural = '07 swagger.'


class LinkGit(BaseClass):
    """Ссылка на git репозиторий."""

    services = models.ForeignKey(DimServices, on_delete=models.PROTECT, related_name='git_services')
    stack = models.ForeignKey(DimTechStack, on_delete=models.PROTECT)
    name = models.ForeignKey(DimServices, on_delete=models.PROTECT, related_name='git_names')
    link_name = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.services}-{self.name}'

    class Meta:
        db_table = f'{db_schema}\".\"link_link_git'
        unique_together = [
            ['name', ]
        ]
        verbose_name = '08 ссылки на репозиторий.'
        verbose_name_plural = '08 ссылки на репозиторий.'
