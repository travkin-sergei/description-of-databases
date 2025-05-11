# views.py
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView
from django.db.models import Count

from ..filters import BaseFilter, SchemaTableFilter, BaseSchemaFilter
from ..models import Base, SchemaTable, BaseSchema, TableColumn


class AboutAppView(TemplateView):
    """Информационная страница о приложении."""
    template_name = "my_metla/about-application.html"


def my_metla_view(request):
    """Тестовая"""
    return HttpResponse("Простая страница my_metla")


class BaseListView(ListView):
    model = Base
    template_name = 'my_metla/database-list.html'
    context_object_name = 'databases'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = BaseFilter(self.request.GET, queryset=queryset)
        return self.filter.qs.select_related('type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context


class BaseSchemaListView(FilterView):
    """Связь баз и схем"""
    model = BaseSchema
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'base_schemas'
    filterset_class = BaseSchemaFilter
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'base',
            'schema',
            'base__type'
        ).prefetch_related(
            'schematable_set__table',
            'schematable_set__table_type'
        ).annotate(
            table_count=Count('schematable')
        ).order_by('base__name', 'schema__name')

        # Применяем фильтр
        self.filter = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список связей База-Схема"
        return context


class SchemaTableListView(ListView):
    """Отображение всех таблиц из всех баз данных"""
    model = BaseSchema
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'base_schemas'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = BaseSchemaFilter(self.request.GET, queryset=queryset)
        return self.filter.qs.select_related(
            'base__type',
            'schema'
        ).prefetch_related(
            'schematable_set__table',
            'schematable_set__table_type'  # Важно: prefetch для table_type
        ).order_by('base__name', 'schema__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        context['title'] = "Список связей База-Схема-Таблица"
        return context



class TableDetailView(DetailView):
    model = SchemaTable
    template_name = 'my_metla/table-detail.html'
    context_object_name = 'schema_table'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все столбцы для этой таблицы
        context['columns'] = TableColumn.objects.filter(
            schema_table=self.object
        ).select_related('column', 'column__type').order_by('numbers')
        return context
