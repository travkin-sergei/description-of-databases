# app_updates/filters.py
import django_filters
from django import forms  # Добавляем импорт форм
from .models import DimUpdateMethod, LinkUpdateCol


class DimUpdateMethodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Название метода',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия'})
    )

    schedule = django_filters.CharFilter(
        field_name='schedule',
        lookup_expr='icontains',
        label='Расписание',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть расписания'})
    )

    has_url = django_filters.BooleanFilter(
        field_name='url',
        lookup_expr='isnull',
        exclude=True,
        label='Имеет URL',
        widget=forms.CheckboxInput()
    )

    url_name = django_filters.CharFilter(
        field_name='url__name',
        lookup_expr='icontains',
        label='Название URL',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия URL'})
    )

    is_active = django_filters.BooleanFilter(
        label='Активен',
        widget=forms.CheckboxInput()  # ИЗМЕНЕНО
    )

    class Meta:
        model = DimUpdateMethod
        fields = ['name', 'schedule', 'url', 'is_active']


class LinkUpdateColFilter(django_filters.FilterSet):
    type_name = django_filters.CharFilter(
        field_name='type__name',
        lookup_expr='icontains',
        label='Название типа',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия метода'})
    )

    main_column = django_filters.CharFilter(
        field_name='main__column__name',
        lookup_expr='icontains',
        label='Основной столбец',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия столбца'})
    )

    sub_column = django_filters.CharFilter(
        field_name='sub__column__name',
        lookup_expr='icontains',
        label='Вторичный столбец',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия столбца'})
    )

    main_table = django_filters.CharFilter(
        field_name='main__table__name',
        lookup_expr='icontains',
        label='Основная таблица',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия таблицы'})
    )

    has_sub = django_filters.BooleanFilter(
        field_name='sub',
        lookup_expr='isnull',
        exclude=True,
        label='Имеет вторичный столбец',
        widget=forms.CheckboxInput()
    )

    is_active = django_filters.BooleanFilter(
        label='Активен',
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = LinkUpdateCol
        fields = ['type', 'main', 'sub', 'is_active']
