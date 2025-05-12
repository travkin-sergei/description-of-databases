# views.py
from django.core.paginator import Paginator
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
    """"""
    model = Base
    template_name = 'my_metla/database-list.html'
    context_object_name = 'databases'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = BaseFilter(self.request.GET, queryset=queryset)
        return self.filter.qs.select_related('type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter

        # Сохраняем параметры фильтрации в пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()

        return context


class BaseSchemaListView(FilterView):
    """Связь баз и схем"""

    model = BaseSchema
    filterset_class = BaseSchemaFilter
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'base_schemas'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'base',  # Получаем объект base
            'base__type',  # Получаем тип базы данных, связанный с base
            'schema'
        ).prefetch_related(
            'schematable_set__table',
            'schematable_set__table_type'
        ).annotate(
            table_count=Count('schematable')
        ).order_by('base__name', 'schema__name')

        # Сохраняем фильтр в контекст
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()  # Добавляем distinct() если есть дубли

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список связей База-Схема"
        # Добавляем фильтр в контекст для формы фильтрации
        context['filter'] = self.filterset
        return context


class TableDetailView(DetailView):
    model = SchemaTable
    template_name = 'my_metla/table-detail.html'
    context_object_name = 'schema_table'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все столбцы для этой таблицы
        context['columns'] = TableColumn.objects.filter(
            schema_table=self.object
        ).select_related('column', 'column__type').order_by('numbers')
        return context


class SchemaTableListView(FilterView):
    model = SchemaTable
    filterset_class = SchemaTableFilter
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'schema_tables'
    paginate_by = 20


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'base_schema__base',
            'base_schema__base__type',
            'base_schema__schema',
            'table',
            'table_type',
        ).order_by(
            'base_schema__base__name',
            'base_schema__schema__name',
            'table__name'
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список связей База-Схема"
        context['filter'] = self.filterset
        return context
