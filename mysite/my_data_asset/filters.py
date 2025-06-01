import django_filters
from .models import Asset, AssetDomain


class AssetDomainFilter(django_filters.FilterSet):
    """Фильтрация доменов данных."""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    link = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AssetDomain
        fields = ['name', 'description', 'res_url']


class AssetFilter(django_filters.FilterSet):
    """Фильтрация источников данных."""
    type = django_filters.CharFilter(field_name='type__name', lookup_expr='icontains')
    domain = django_filters.CharFilter(field_name='domain__name', lookup_expr='icontains')
    details = django_filters.CharFilter(field_name='details__name', lookup_expr='icontains')
    version = django_filters.CharFilter(lookup_expr='icontains')
    res_url = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Asset
        fields = ['type', 'domain', 'details', 'version', 'res_url']
