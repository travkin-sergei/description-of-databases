import django_filters
from my_request.models import ColumnFZ, FZ
from my_dbm.models import LinkColumn


class ColumnFZFilter(django_filters.FilterSet):
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
        model = ColumnFZ
        fields = [
            'column__table__schema__base__name',
            'column__table__schema__schema',
            'column__table__name',
            'column__columns',
            'fz__name',
        ]