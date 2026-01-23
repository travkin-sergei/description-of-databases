# app_updates/filters.py
import django_filters
from .models import DimUpdateMethod, LinkUpdateCol


class DimUpdateMethodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название метода'
    )
    schedule = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Расписание'
    )
    has_url = django_filters.BooleanFilter(
        field_name='url',
        lookup_expr='isnull',
        exclude=True,
        label='Имеет URL'
    )
    url_name = django_filters.CharFilter(
        field_name='url__name',
        lookup_expr='icontains',
        label='Название URL'
    )

    class Meta:
        model = DimUpdateMethod
        fields = ['name', 'schedule', 'url', 'is_active']


class LinkUpdateColFilter(django_filters.FilterSet):
    type_name = django_filters.CharFilter(
        field_name='type__name',
        lookup_expr='icontains',
        label='Название типа'
    )
    main_column = django_filters.CharFilter(
        field_name='main__column__name',
        lookup_expr='icontains',
        label='Основной столбец'
    )
    sub_column = django_filters.CharFilter(
        field_name='sub__column__name',
        lookup_expr='icontains',
        label='Вторичный столбец'
    )
    main_table = django_filters.CharFilter(
        field_name='main__table__name',
        lookup_expr='icontains',
        label='Основная таблица'
    )
    has_sub = django_filters.BooleanFilter(
        field_name='sub',
        lookup_expr='isnull',
        exclude=True,
        label='Имеет вторичный столбец'
    )
    is_active = django_filters.BooleanFilter(
        label='Активен'
    )

    class Meta:
        model = LinkUpdateCol
        fields = ['type', 'main', 'sub', 'is_active']