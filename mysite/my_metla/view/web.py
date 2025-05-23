from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView
from django.db.models import Prefetch, Count

from ..filters import BaseFilter, SchemaTableFilter, BaseSchemaFilter
from ..models import Base, SchemaTable, BaseSchema, TableColumn


class BaseViewMixin:
    """Base mixin for common view functionality."""

    def get_filter_params(self):
        """Get filter parameters without 'page' for pagination."""
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            get_copy.pop('page')
        return get_copy.urlencode()


class AboutAppView(TemplateView):
    """Информационная страница о приложении."""
    template_name = "my_metla/about-application.html"


def my_metla_view(request):
    """Тестовая"""
    return HttpResponse("Простая страница my_metla")


class BaseListView(LoginRequiredMixin, BaseViewMixin, ListView):
    """Список баз данных."""
    model = Base
    template_name = 'my_metla/database-list.html'
    context_object_name = 'databases'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('name', 'type')  # Только допустимые связи
        self.filter = BaseFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'filter': self.filter,
            'get_params': self.get_filter_params()
        })
        return context


class BaseSchemaListView(LoginRequiredMixin, BaseViewMixin, FilterView):
    """Связь баз и схем"""
    model = BaseSchema
    filterset_class = BaseSchemaFilter
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'base_schemas'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'base',
            'base__type',
            'schema'
        ).prefetch_related(
            'schematable_set__table',
            'schematable_set__table_type'
        ).annotate(
            table_count=Count('schematable')
        ).order_by('base__name', 'schema__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Список связей База-Схема"
        return context


class SchemaTableListView(LoginRequiredMixin, FilterView):
    """Список таблиц с фильтрацией"""
    model = SchemaTable
    filterset_class = SchemaTableFilter
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'schema_tables'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'alias', 'table', 'table_type'
        ).order_by('table__name').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()
        return context


class TableDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о таблице"""
    model = SchemaTable
    template_name = 'my_metla/table-detail.html'
    context_object_name = 'schema_table'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'alias',
            'table',
            'table_type',
        ).prefetch_related(
            'tablecolumn_set',
            'tablecolumn_set__name',
            'tablecolumn_set__type',
            'alias__baseschema_set__env'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_table = self.object

        # Получаем все связанные записи SchemaTable с той же таблицей
        related_tables = SchemaTable.objects.filter(
            table=current_table.table
        ).select_related(
            'alias',
            'table',
            'table_type'
        ).prefetch_related(
            'tablecolumn_set',
            'alias__baseschema_set__env'
        )

        # Собираем данные об окружениях
        environments = set()
        columns_data = []

        # Собираем информацию о столбцах
        for column in current_table.tablecolumn_set.all():
            column_envs = set()
            for table in related_tables:
                if table.alias and hasattr(table.alias, 'baseschema_set'):
                    for base_schema in table.alias.baseschema_set.all():
                        if base_schema.env:
                            column_envs.add(base_schema.env)

            columns_data.append({
                'column': column,
                'environments': list(column_envs)
            })

            # Добавляем среды в общий список
            environments.update(column_envs)

        context.update({
            'title': f"Детали таблицы {current_table.table.name}",
            'table_environments': environments,
            'columns_data': columns_data,
            'related_tables': related_tables
        })
        return context
