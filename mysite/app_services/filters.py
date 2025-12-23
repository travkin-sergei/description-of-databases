# filters.py
import django_filters
from django_filters import CharFilter, BooleanFilter, ModelChoiceFilter
from django.db.models import Q

from app_dbm.models import DimStage

from .models import (
    DimLink,
    DimTechStack,
    DimServices, DimServicesTypes
)


class DimServicesFilter(django_filters.FilterSet):
    """Список сервисов с фильтрацией по синонимам"""

    search = CharFilter(method='filter_search', label='Поиск')
    type = ModelChoiceFilter(
        queryset=DimServicesTypes.objects.all(),
        field_name='type',
        label='Тип сервиса',
        to_field_name='id'
    )
    is_active = BooleanFilter(field_name='is_active', label='Активен')

    class Meta:
        model = DimServices
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(alias__icontains=value) |  # поиск по alias в DimServices
            Q(type__name__icontains=value) |  # поиск по type в DimServices
            Q(dimservicesname__name__icontains=value)  # поиск по name в DimServicesName
        ).distinct()


class DimLinkFilter(django_filters.FilterSet):
    """Фильтры ссылок."""

    link = django_filters.CharFilter(lookup_expr='icontains', label='Ссылка содержит')
    link_name = django_filters.CharFilter(lookup_expr='icontains', label='Название ссылки содержит')
    description = django_filters.CharFilter(lookup_expr='icontains', label='Описание ссылки содержит')
    status_code = django_filters.CharFilter(lookup_expr='icontains', label='Статус код')
    stack = django_filters.ModelChoiceFilter(
        queryset=DimTechStack.objects.all(),
        label='Технологический стек',
        field_name='stack',
        to_field_name='id',
    )

    stage = django_filters.ModelChoiceFilter(
        queryset=DimStage.objects.all(),
        label='Стадия проекта',
        field_name='stage',
        to_field_name='id'
    )

    class Meta:
        model = DimLink
        fields = ['link', 'link_name', 'stack', 'stage', 'service', 'status_code', 'description', ]
