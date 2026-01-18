# app_request/filters.py
import django_filters
from .models import TableGroup, ColumnGroup


class ColumnGroupFilter(django_filters.FilterSet):
    # Обратите внимание: если в модели LinkColumn нет поля 'name',
    # используйте правильное имя поля, например 'columns'

    # Фильтры должны соответствовать реальным полям в модели
    column__table__schema__base__name = django_filters.CharFilter(
        field_name='column__table__schema__base__name',
        lookup_expr='icontains',
        label='База данных'
    )

    column__table__schema__schema = django_filters.CharFilter(
        field_name='column__table__schema__schema',
        lookup_expr='icontains',
        label='Схема'
    )

    column__table__name = django_filters.CharFilter(
        field_name='column__table__name',
        lookup_expr='icontains',
        label='Таблица'
    )

    column__columns = django_filters.CharFilter(
        field_name='column__columns',  # Используем 'columns' вместо 'name'
        lookup_expr='icontains',
        label='Столбец'
    )

    group_name__name = django_filters.CharFilter(
        field_name='group_name__name',
        lookup_expr='icontains',
        label='Закон'
    )

    class Meta:
        model = ColumnGroup
        fields = [
            'column__table__schema__base__name',
            'column__table__schema__schema',
            'column__table__name',
            'column__columns',  # Исправлено с column__name на column__columns
            'group_name__name',
        ]

    @property
    def qs(self):
        queryset = super().qs
        return queryset.order_by('group_name__name', 'column__columns')


class TableGroupFilter(django_filters.FilterSet):
    # Фильтры для связанных полей, аналогично ColumnGroupFilter

    table__schema__base__name = django_filters.CharFilter(
        field_name='table__schema__base__name',
        lookup_expr='icontains',
        label='База данных'
    )

    table__schema__schema = django_filters.CharFilter(
        field_name='table__schema__schema',
        lookup_expr='icontains',
        label='Схема'
    )

    table__name = django_filters.CharFilter(
        field_name='table__name',
        lookup_expr='icontains',
        label='Таблица'
    )

    group_name__name = django_filters.CharFilter(
        field_name='group_name__name',
        lookup_expr='icontains',
        label='Название группы таблиц'
    )

    class Meta:
        model = TableGroup
        fields = [
            'table__schema__base__name',
            'table__schema__schema',
            'table__name',
            'group_name__name',
        ]

    @property
    def qs(self):
        queryset = super().qs
        return queryset.order_by('group_name__name', 'table__name')
