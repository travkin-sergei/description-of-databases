import django_filters
from django_filters import CharFilter, AllValuesFilter, BooleanFilter
from django.db.models import Q
from .models import (
    DimServices,
)


class DimServicesFilter(django_filters.FilterSet):
    """Список сервисов с фильтрацией по синонимам"""

    search = CharFilter(method='filter_search', label='Поиск')
    type = CharFilter(field_name='type__name', lookup_expr='icontains', label='Тип')
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
