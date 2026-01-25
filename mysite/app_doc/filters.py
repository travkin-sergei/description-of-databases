# app_doc/filters.py
from django_filters import rest_framework as filters
from .models import DimDocType, DimDoc


class DocTypeFilter(filters.FilterSet):
    """
    Фильтр для модели DimDocType (типы документов).
    """
    name = filters.CharFilter(
        lookup_expr='icontains',
        label='Название типа (частичное совпадение)'
    )
    description = filters.CharFilter(
        lookup_expr='icontains',
        label='Описание (частичное совпадение)'
    )

    ordering = filters.OrderingFilter(
        fields={
            'name': 'name',
            'id': 'id',
        },
        field_labels={
            'name': 'Название типа',
            'id': 'ID типа'
        },
        label='Сортировка'
    )

    class Meta:
        model = DimDocType
        fields = []  # Поля объявлены явно выше, дублировать не нужно


class DocFilter(filters.FilterSet):
    """
    Фильтр для модели DimDoc (документы).
    """
    # Поиск по названию документа
    number = filters.CharFilter(
        lookup_expr='icontains',
        label='Название документа (частичное совпадение)'
    )

    # Фильтрация по типу документа
    doc_type = filters.ModelChoiceFilter(
        queryset=DimDocType.objects.all(),
        label='Тип документа',
        empty_label='Все типы'
    )
    doc_type__name = filters.CharFilter(
        field_name='doc_type__name',
        lookup_expr='icontains',
        label='Название типа документа (частичное совпадение)'
    )

    # Диапазон дат действия
    date_start = filters.DateFilter(
        lookup_expr='gte',
        label='Дата начала ≥'
    )
    date_stop = filters.DateFilter(
        lookup_expr='lte',
        label='Дата окончания ≤'
    )
    date_range = filters.DateFromToRangeFilter(
        field_name='date_start',
        label='Диапазон дат начала (от–до)'
    )

    # Поиск по описанию
    description = filters.CharFilter(
        lookup_expr='icontains',
        label='Описание (частичное совпадение)'
    )

    # Сортировка
    ordering = filters.OrderingFilter(
        fields={
            'number': 'number',
            'date_start': 'date_start',
            'date_stop': 'date_stop',
            'doc_type__name': 'doc_type_name',
        },
        field_labels={
            'number': 'Название документа',
            'date_start': 'Дата начала',
            'date_stop': 'Дата окончания',
            'doc_type_name': 'Тип документа'
        },
        label='Сортировка'
    )

    class Meta:
        model = DimDoc
        fields = []
