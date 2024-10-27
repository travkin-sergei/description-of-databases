import django_filters
from django_filters import CharFilter
from .models import *


class ArticleFilter(django_filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains', )
    content = CharFilter(field_name='content', lookup_expr='icontains', )

    class Meta:
        model = Article
        fields = '__all__'

        def filter_queryset(self, queryset):
            return queryset.filter()