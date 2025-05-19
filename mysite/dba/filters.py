import django_filters
from django_filters import CharFilter, AllValuesFilter
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
    """Основной экран фильтрации"""

    base = AllValuesFilter(field_name='schema_id__base_id__table_catalog', )
    schema = AllValuesFilter(field_name='schema_id__table_schema', )
    table_name = CharFilter(field_name='table_name', lookup_expr='icontains', )
    table_ru = CharFilter(field_name='table_ru', lookup_expr='icontains', )
    is_active = AllValuesFilter(field_name='is_active', )

    class Meta:
        model = Table
        fields = '__all__'

        def filter_queryset(self, queryset):
            return queryset.filter()


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
