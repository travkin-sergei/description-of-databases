from django.db.models import Q
from django.http import HttpResponseNotFound

from django.views import View
from django.views.generic import (
    DetailView, TemplateView,
)
from django_filters.views import FilterView

from ..filters import (
    LinkDBFilter,
    LinkDBTableFilter, LinkColumnFilter,
)
from ..models import (
    DimDB,
    LinkDB,
    LinkDBTable,
    LinkColumnColumn, LinkColumn, LinkColumnName, LinkColumnStage, LinkDBTableName,
)
from my_services.models import LinkServicesTable
from django.contrib.auth.mixins import LoginRequiredMixin

from my_updates.models import LinkUpdate


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'my_dbm/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DatabasesView(LoginRequiredMixin, FilterView):
    """Список баз данных с фильтрацией."""

    model = LinkDB
    filterset_class = LinkDBFilter
    template_name = 'my_dbm/databases.html'
    context_object_name = 'databases'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('stage').order_by('alias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = LinkDB.objects.count()

        # Параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        return context


# не вижу смысла в детализации
# class DatabaseDetailView(LoginRequiredMixin, DetailView):
#     """Детализация базы данных."""
#
#     model = DimDB
#     template_name = 'my_dbm/databases-detail.html'
#     context_object_name = 'database'


class TablesView(LoginRequiredMixin, FilterView):
    model = LinkDBTable
    template_name = 'my_dbm/tables.html'
    context_object_name = 'tables'
    paginate_by = 20
    filterset_class = LinkDBTableFilter

    def get_queryset(self):
        return LinkDBTable.objects.select_related(
            'schema',
            'schema__base',
            'type'
        ).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        return context


class TableDetailView(LoginRequiredMixin, DetailView):
    """Детализация таблицы."""

    model = LinkDBTable
    template_name = 'my_dbm/tables-detail.html'
    context_object_name = 'tables'

    def get_queryset(self):
        return LinkDBTable.objects.select_related(
            'schema', 'schema__base', 'type'
        ).prefetch_related(
            'linkcolumn_set__linkcolumnstage_set__stage'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.object

        # Существующие столбцы
        columns = table.linkcolumn_set.filter(is_active=True).order_by('unique_together', 'date_create', 'id')
        context['columns'] = columns

        # Связи между столбцами
        context['column_relations'] = LinkColumnColumn.objects.filter(
            Q(main__in=columns) | Q(sub__in=columns)
        ).select_related('main', 'sub', 'type')

        # Сервисы
        services = LinkServicesTable.objects.filter(table=table).select_related('service')
        context['services_list'] = services
        context['services_count'] = services.count()

        # Расписания обновлений
        schedules = LinkUpdate.objects.filter(
            column__main__table=table
        ).values(
            'name__id',
            'name__name',
            'name__schedule',
            'name__is_active'
        ).distinct().order_by('name__name')
        context['schedules'] = schedules

        # === Новое: альтернативные имена таблицы ===
        alt_names = LinkDBTableName.objects.filter(table=table)
        context['alt_table_names'] = alt_names

        return context


class ColumnListView(LoginRequiredMixin, FilterView):
    """Список столбцов с фильтрацией и пагинацией."""

    model = LinkColumn
    filterset_class = LinkColumnFilter
    template_name = 'my_dbm/columns.html'
    context_object_name = 'columns'
    paginate_by = 20

    def get_queryset(self):
        return (
            LinkColumn.objects
            .filter(is_active=True)
            .select_related(
                'table',
                'table__schema',
                'table__schema__base',
                'table__type',
            ).order_by('table__name', 'columns')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Для пагинации с сохранением параметров фильтрации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        return context


class ColumnDetailView(LoginRequiredMixin, DetailView):
    """
    Детализация столбца.
    """
    model = LinkColumn
    template_name = 'my_dbm/columns-detail.html'
    context_object_name = 'column'

    def get_queryset(self):
        return LinkColumn.objects.select_related(
            'table',
            'table__schema',
            'table__schema__base',
            'table__type'
        ).prefetch_related(
            'linkcolumnname_set__name',
            'linkcolumnstage_set__stage'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column = self.object

        # Получить связи столбца (главный или подчинённый)
        column_relations = LinkColumnColumn.objects.filter(
            Q(main=column) | Q(sub=column)
        ).select_related('main', 'sub', 'type')
        context['column_relations'] = column_relations

        # Синонимы названий столбцов
        column_names = LinkColumnName.objects.filter(column=column).select_related('name')
        context['column_names'] = column_names

        # Стадии стендов
        stages = LinkColumnStage.objects.filter(column=column).select_related('stage')
        context['stages'] = stages

        # Обновления
        schedules = LinkUpdate.objects.filter(
            column__main=column
        ).values(
            'name__id',
            'name__name',
            'name__schedule',
            'name__is_active'
        ).distinct().order_by('name__name')
        context['schedules'] = schedules

        return context
