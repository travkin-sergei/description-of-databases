import django_filters
from django_filters import CharFilter, AllValuesFilter
from django.db.models import Q
from .models import *

class BaseGroupFilter(django_filters.FilterSet):
    table_catalog = CharFilter(field_name='table_catalog', lookup_expr='icontains', )

    class Meta:
        model = BaseGroup
        # fields = 'table_catalog',
        exclude = ['created_at', 'updated_at', 'hash_address']


class FunctionFilter(django_filters.FilterSet):
    name_fun = CharFilter(field_name='name_fun', lookup_expr='icontains', )
    schema = CharFilter(field_name='schema_id__name', lookup_expr='icontains', )
    base = AllValuesFilter(field_name='schema_id__base_id__table_catalog', )
    is_active = AllValuesFilter(field_name='is_active', )

    class Meta:
        model = Function
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']


class TableFilter(django_filters.FilterSet):
    """Фильтр для таблиц с поддержкой поиска по связанным именам"""

    table_catalog = django_filters.CharFilter(
        field_name='schema__base__table_catalog',
        lookup_expr='icontains',
        label='База данных'
    )

    schema = django_filters.CharFilter(
        field_name='schema__table_schema',
        lookup_expr='icontains',
        label='Схема'
    )

    table_name = django_filters.CharFilter(
        method='filter_by_table_name',
        label='Имя таблицы'
    )

    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Активна'
    )

    class Meta:
        model = Table
        fields = []

    def filter_by_table_name(self, queryset, name, value):
        """
        Фильтрация по имени таблицы (основному или связанным именам из TableName)
        """
        return queryset.filter(
            Q(table_name__icontains=value) |
            Q(names__name__icontains=value)
        ).distinct()


class ColumnFilter(django_filters.FilterSet):
    """Основной экран фильтрация"""

    schema = CharFilter(field_name='table_id__schema_id__table_schema', lookup_expr='icontains', )
    table = CharFilter(field_name='table_id__table_name', lookup_expr='icontains', )
    column_name = CharFilter(field_name='column_name', lookup_expr='icontains', )
    column_com = CharFilter(field_name='column_com', lookup_expr='icontains', )
    is_active = AllValuesFilter(field_name='is_active', )

    class Meta:
        model = Column
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']


class UpdateFilter(django_filters.FilterSet):
    """Описать фильтры сейчас работают не корректно"""

    name = CharFilter(field_name='name', lookup_expr='icontains', )
    description = CharFilter(field_name='description', lookup_expr='icontains', )
    schedule = AllValuesFilter(field_name='schedule', )
    is_active = AllValuesFilter(field_name='is_active', )

    class Meta:
        model = Update
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']


class StageColumnFilter(django_filters.FilterSet):
    stage = AllValuesFilter(field_name='stage_id__type_id__name', )

    class Meta:
        model = StageColumn
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']


class ServiceFilter(django_filters.FilterSet):
    """Список сервисов"""

    service = CharFilter(field_name='service', lookup_expr='icontains', )

    class Meta:
        model = Service
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']


class ServiceTableFilter(django_filters.FilterSet):
    # stage = AllValuesFilter(field_name='stage_id__type_id__name', )

    class Meta:
        model = StageColumn
        fields = '__all__'
        # exclude = ['time_create', 'time_update', 'is_published']
