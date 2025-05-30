import django_filters
from django_filters import FilterSet, CharFilter, ModelChoiceFilter, BooleanFilter
from django import forms
from django.db.models import Q

from .models import (
    Environment,
    Base,
    SchemaTable,
    BaseType,
    TableType,
)


class BaseFilter(FilterSet):
    name = CharFilter(
        field_name='name__name',
        lookup_expr='icontains',
        label='Название базы',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Поиск по названию базы',
        })
    )

    type = ModelChoiceFilter(
        field_name='type',
        queryset=BaseType.objects.all(),
        label='Тип базы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    env = ModelChoiceFilter(
        field_name='env',
        queryset=Environment.objects.all(),
        label='Окружение',
        widget=forms.Select(
            attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    is_active = BooleanFilter(
        field_name='is_active',
        label='Активные',
        widget=forms.Select(
            choices=[
                ('', 'Все'),
                ('true', 'Активные'),
                ('false', 'Неактивные')
            ],
            attrs={
                'class': 'form-select bg-black text-white',
            }
        )
    )

    class Meta:
        model = Base
        fields = ['name', 'type', 'env', 'is_active']




class SchemaTableFilter(django_filters.FilterSet):
    alias__base = django_filters.CharFilter(
        field_name='alias__base',
        lookup_expr='icontains',
        label='База данных',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Название базы',
        })
    )

    alias__schema = django_filters.CharFilter(
        field_name='alias__schema',
        lookup_expr='icontains',
        label='Схема',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Название схемы',
        })
    )

    table__name = django_filters.CharFilter(
        field_name='table__name',
        lookup_expr='icontains',
        label='Таблица',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Название таблицы',
        })
    )

    table_type = django_filters.ModelChoiceFilter(
        field_name='table_type',
        queryset=TableType.objects.all(),
        label='Тип таблицы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    table_is_metadata = django_filters.BooleanFilter(
        field_name='table_is_metadata',
        label='Только метаданные',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input custom-checkbox',
        })
    )

    class Meta:
        model = SchemaTable
        fields = ['alias__base', 'alias__schema', 'table__name', 'table_type', 'table_is_metadata']
