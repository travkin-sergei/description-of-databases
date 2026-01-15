# app_dbm/autocomplete.py
from dal import autocomplete
from .models import LinkColumn, DimTypeLink
from django.urls import path


class ColumnAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Не показывать результаты, если нет поискового запроса
        if not self.q:
            return LinkColumn.objects.none()

        qs = LinkColumn.objects.select_related(
            'table__schema__base'
        ).filter(columns__icontains=self.q)

        return qs[:100]  # Ограничиваем результаты для производительности

    def get_result_label(self, item):
        # Кастомное отображение
        try:
            return f"{item.columns} ({item.table.schema.base.name}.{item.table.name})"
        except AttributeError:
            return item.columns


class TypeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.q:
            return DimTypeLink.objects.none()

        qs = DimTypeLink.objects.filter(name__icontains=self.q)
        return qs[:50]


app_name = 'dbm_autocomplete'

urlpatterns = [
    path(
        'column-autocomplete/',
        ColumnAutocomplete.as_view(),  # Теперь это ваш класс
        name='column-autocomplete'
    ),
    path(
        'type-autocomplete/',
        TypeAutocomplete.as_view(),
        name='type-autocomplete'
    ),
]
