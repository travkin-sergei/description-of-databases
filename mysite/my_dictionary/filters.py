import django_filters
from django.db.models import Q

from .models import DimDictionary


class DictionaryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_by_name_or_synonym", label="Поиск")

    class Meta:
        model = DimDictionary
        fields = []

    def search_by_name_or_synonym(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(synonyms__synonym__icontains=value)  # ← Используем related_name
        ).distinct()  # Убираем дубликаты