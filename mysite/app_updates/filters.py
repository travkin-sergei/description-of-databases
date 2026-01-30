# app_updates/filters.py
import django_filters
from django import forms
from .models import DimUpdateMethod, LinkUpdateCol


def filter_url_text(queryset, name, value):
    if not value:
        return queryset
    return queryset.filter(url__url__icontains=value)


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

    url_text = django_filters.CharFilter(
        method=filter_url_text,  # ← ИСПОЛЬЗУЕМ method
        label='Содержимое URL',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть URL'})
    )

    class Meta:
        model = DimUpdateMethod
        fields = ['name', 'schedule']
