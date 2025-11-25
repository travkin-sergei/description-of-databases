import django_filters
from .models import DimUpdateMethod


class DimUpdateMethodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название метода'
    )
    schedule = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Расписание'
    )
    link_code = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Ссылка на код'
    )

    class Meta:
        model = DimUpdateMethod
        fields = [
            'name',
            'schedule',
            'link_code',
            'is_active',
        ]