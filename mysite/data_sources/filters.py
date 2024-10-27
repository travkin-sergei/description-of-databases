import django_filters
from django_filters import CharFilter
from .models import *


class DataSourcesFilter(django_filters.FilterSet):
    slag = CharFilter(field_name='slag', lookup_expr='icontains', )
    link_sources = CharFilter(field_name='link_sources', lookup_expr='icontains', )
    doc_regulatory = CharFilter(field_name='doc_regulatory', lookup_expr='icontains', )
    name_sources = CharFilter(field_name='name_sources', lookup_expr='icontains', )
    description = CharFilter(field_name='description', lookup_expr='icontains', )

    class Meta:
        model = DataSources
        fields = 'slag', 'link_sources', 'doc_regulatory', 'name_sources', 'description',
