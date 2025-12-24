import django_filters

from .models import ColumnGroup


class ColumnGroupFilter(django_filters.FilterSet):
    """
    Фильтрация по 152 ФЗ
    """
    column__table__schema__base__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='База данных'
    )
    column__table__schema__schema = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Схема'
    )
    column__table__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Таблица'
    )
    column__columns = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Столбец'
    )
    fz__name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Закон'
    )

    class Meta:
        model = ColumnGroup
        fields = [
            'column__table__schema__base__name',
            'column__table__schema__schema',
            'column__table__name',
            'column__columns',
            'fz__name',
        ]