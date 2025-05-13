# filters.py
from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    ModelChoiceFilter,
)
from django import forms

from .models import (
    Base,
    SchemaTable,
    BaseSchema, BaseType, TableType,
)


class BaseFilter(FilterSet):
    """Фильтрация баз данных."""

    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Название',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Введите имя базы',
        })
    )
    type = ChoiceFilter(
        field_name='type__name',
        label='Тип базы данных',
        choices=[],
        empty_label='Все типы',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Введите тип базы данных',
        })
    )

    is_active = ChoiceFilter(
        field_name='is_active',
        label='Статус активности',
        choices=[],
        empty_label='Все статусы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
            'placeholder': 'Введите статус',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Получаем исходный queryset (без фильтрации)
        queryset = self.queryset if hasattr(self, 'queryset') and self.queryset is not None else Base.objects.all()

        # Уникальные типы из исходного queryset
        types = queryset.order_by('type__name').values_list('type__name', flat=True).distinct()
        self.filters['type'].extra['choices'] = [(t, t) for t in types if t]

        # Уникальные статусы активности из исходного queryset
        statuses = queryset.order_by('is_active').values_list('is_active', flat=True).distinct()
        status_choices = []
        if True in statuses:
            status_choices.append((True, 'Активные'))
        if False in statuses:
            status_choices.append((False, 'Неактивные'))
        self.filters['is_active'].extra['choices'] = status_choices

    class Meta:
        model = Base
        fields = ['name', 'type', 'is_active']


class SchemaTableFilter(FilterSet):
    base__name = CharFilter(
        field_name='base_schema__base__name',
        lookup_expr='icontains',
        label='База данных',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Название базы',
        })
    )

    schema__name = CharFilter(
        field_name='base_schema__schema__name',
        lookup_expr='icontains',
        label='Схема',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Название схемы',
        })
    )

    table__name = CharFilter(
        field_name='table__name',
        lookup_expr='icontains',
        label='Таблица',
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-white',
            'placeholder': 'Название таблицы',
        })
    )

    base__type = ModelChoiceFilter(
        field_name='base_schema__base__type',
        queryset=BaseType.objects.all(),
        label='Тип базы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    table_type = ModelChoiceFilter(
        field_name='table_type',
        queryset=TableType.objects.filter(is_active=True),
        label='Тип таблицы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    class Meta:
        model = SchemaTable
        fields = ['base__name', 'schema__name', 'base__type', 'table__name', 'table_type']


class BaseSchemaFilter(FilterSet):
    base__name = CharFilter(
        lookup_expr='icontains',
        label='База данных',
        widget=forms.TextInput(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    schema__name = CharFilter(
        lookup_expr='icontains',
        label='Схема',
        widget=forms.TextInput(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    table__name = CharFilter(
        field_name='schematable__table__name',
        lookup_expr='icontains',
        label='Таблица',
        widget=forms.TextInput(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    base__type = ModelChoiceFilter(
        queryset=BaseType.objects.all(),
        label='Тип базы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    table_type = ModelChoiceFilter(
        method='filter_by_table_type',
        queryset=TableType.objects.all(),
        label='Тип таблицы',
        widget=forms.Select(attrs={
            'class': 'form-select bg-black text-white',
        })
    )

    def filter_by_table_type(self, queryset, name, value):
        return queryset.filter(schematable__table_type=value).distinct()

    class Meta:
        model = BaseSchema
        fields = ['base__name', 'schema__name', 'base__type', 'table__name', 'table_type']
