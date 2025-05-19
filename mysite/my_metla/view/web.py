# views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView
from django.db.models import Prefetch, Count

from ..filters import BaseFilter, SchemaTableFilter, BaseSchemaFilter
from ..models import Base, SchemaTable, BaseSchema, TableColumn


class AboutAppView(TemplateView):
    """Информационная страница о приложении."""
    template_name = "my_metla/about-application.html"


def my_metla_view(request):
    """Тестовая"""
    return HttpResponse("Простая страница my_metla")


class BaseListView(LoginRequiredMixin, ListView):
    """Список баз данных."""

    model = Base
    template_name = 'my_metla/database-list.html'
    context_object_name = 'databases'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = BaseFilter(self.request.GET, queryset=queryset)
        return self.filter.qs.select_related('type', 'env')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter

        # Сохраняем параметры фильтрации в пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['get_params'] = get_params.urlencode()

        return context


class BaseSchemaListView(LoginRequiredMixin, FilterView):
    """Связь баз и схем"""

    model = BaseSchema
    filterset_class = BaseSchemaFilter
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'base_schemas'
    paginate_by = 20

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


class SchemaTableListView(LoginRequiredMixin, FilterView):
    """Список уникальных таблиц"""
    model = SchemaTable
    filterset_class = SchemaTableFilter
    template_name = 'my_metla/schema-tables.html'
    context_object_name = 'schema_tables'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'base_schema__base__type',
            'base_schema__base__name',
            'base_schema__schema',
            'table',
            'table_type',
        ).prefetch_related(
            'base_schema__base__env'
        ).annotate(
            env_count=Count('base_schema__base__env', distinct=True),
        ).order_by(
            'base_schema__base__type__name',
            'base_schema__base__name__name',
            'base_schema__schema__name',
            'table__name'
        ).distinct()

        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Сохраняем параметры фильтрации для пагинации
        get_copy = self.request.GET.copy()
        if 'page' in get_copy:
            del get_copy['page']
        context['get_params'] = get_copy.urlencode()
        context['title'] = "Список таблиц"
        return context


class TableDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о таблице со всеми связанными данными."""

    model = SchemaTable
    template_name = 'my_metla/table-detail.html'
    context_object_name = 'schema_table'
    pk_url_kwarg = 'pk'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related(
            'base_schema__base',
            'base_schema__base__type',
            'base_schema__base__env',
            'base_schema__schema',
            'table',
            'table_type',
        ).prefetch_related(
            Prefetch(
                'tablecolumn_set',
                queryset=TableColumn.objects.select_related(
                    'column',
                    'column__type'
                ).order_by('numbers')
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущую таблицу
        current_table = self.object.table

        # Находим все SchemaTable, где встречается эта таблица
        all_schema_tables = SchemaTable.objects.filter(table=current_table).select_related(
            'base_schema__base__env'
        ).prefetch_related(
            'tablecolumn_set__column'
        )

        # Собираем все окружения, где есть эта таблица
        table_environments = list(set(
            st.base_schema.base.env for st in all_schema_tables
        ))

        # Собираем информацию о столбцах и их окружениях
        columns_data = []
        for column in self.object.tablecolumn_set.all():
            # Находим все SchemaTable, где есть этот столбец
            column_schema_tables = SchemaTable.objects.filter(
                table=current_table,
                tablecolumn__column=column.column
            ).select_related('base_schema__base__env')

            # Получаем уникальные окружения для этого столбца
            column_environments = list(set(
                st.base_schema.base.env for st in column_schema_tables
            ))

            columns_data.append({
                'column': column,
                'environments': column_environments,
            })

        context.update({
            'title': f"Детали таблицы {self.object.table.name}",
            'table_environments': table_environments,
            'columns_data': columns_data,
        })
        return context
