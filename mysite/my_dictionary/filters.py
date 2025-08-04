import django_filters
from .models import DimDictionary


class DictionaryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category__name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = DimDictionary
        fields = ['name', 'category__name', 'description']