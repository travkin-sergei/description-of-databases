# app_dbm/filters.py
import django_filters
from django_filters import CharFilter, ModelChoiceFilter
from django import forms
from django.db.models import Q
from .models import (
    DimStage, LinkDB, LinkSchema, LinkTable, LinkColumn
)


class LinkDBFilter(django_filters.FilterSet):
    """
    Фильтр для модели LinkDB.
    Позволяет фильтровать по базе данных, алиасу, хосту, порту, стенду и активности.
    """

    db_name = CharFilter(field_name='base__name', lookup_expr='icontains', label='Имя базы данных')
    alias = CharFilter(field_name='alias', lookup_expr='icontains', label='Алиас')
    host = CharFilter(field_name='host', lookup_expr='icontains', label='Хост')
    port = CharFilter(field_name='port', lookup_expr='icontains', label='Порт')
    is_active = django_filters.BooleanFilter(widget=None)
    stage = ModelChoiceFilter(
        field_name='stage',
        queryset=DimStage.objects.all(),
        label='Стенд',
        empty_label='Все стенды'
    )

    class Meta:
        model = LinkDB
        fields = ['db_name', 'alias', 'host', 'port', 'stage', 'is_active']


class LinkSchemaFilter(django_filters.FilterSet):
    """
    Фильтр для модели LinkSchema.
    """
    base = django_filters.CharFilter(
        field_name='base__name',
        lookup_expr='icontains',
        label='База данных',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-dark',
            'placeholder': 'База данных...'
        })
    )
    schema = django_filters.CharFilter(
        field_name='schema',
        lookup_expr='icontains',
        label='Схема',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-dark',
            'placeholder': 'Схема...'
        })
    )

    class Meta:
        model = LinkSchema
        fields = ['base', 'schema']


class LinkTableFilter(django_filters.FilterSet):
    table_catalog = django_filters.CharFilter(
        field_name='schema__base__name',
        lookup_expr='icontains',
        label='Каталог'
    )
    schema = django_filters.CharFilter(
        field_name='schema__schema',
        lookup_expr='icontains',
        label='Схема'
    )
    table_name = django_filters.CharFilter(method='filter_table_name')
    is_active = django_filters.BooleanFilter()
    is_metadata = django_filters.BooleanFilter()

    class Meta:
        model = LinkTable
        fields = ['table_catalog', 'schema', 'table_name', 'is_active', 'is_metadata']

    def filter_table_name(self, queryset, name, value):
        """
        Фильтрует по основному имени таблицы ИЛИ по альтернативному имени
        """
        if value:
            # Фильтруем по основному имени таблицы ИЛИ по альтернативному имени
            return queryset.filter(
                Q(name__icontains=value) |
                Q(linktablename__name__icontains=value)
            ).distinct()
        return queryset


class LinkColumnFilter(django_filters.FilterSet):
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
    columns = django_filters.CharFilter(
        field_name='columns',
        lookup_expr='icontains',
        label='Колонка'
    )
    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        label='Описание'
    )

    class Meta:
        model = LinkColumn
        fields = [
            'table__schema__base__name',
            'table__schema__schema',
            'table__name',
            'columns',
            'description'
        ]
