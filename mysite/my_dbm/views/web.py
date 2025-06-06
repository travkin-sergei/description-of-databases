from django.db.models import Q
from django.http import HttpResponseNotFound

from django.views import View
from django.views.generic import (
    DetailView, TemplateView,
)
from django_filters.views import FilterView

from ..filters import (
    LinkDBFilter,
    LinkDBTableFilter,
)
from ..models import (
    DimDB,
    LinkDB,
    LinkDBTable,
    LinkColumnColumn,
)
from my_services.models import LinkServicesTable
from django.contrib.auth.mixins import LoginRequiredMixin


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
        # Правильный select_related только для связанных моделей
        return queryset.select_related('stage').order_by('alias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = LinkDB.objects.count()  # Исправлено с DimDB на LinkDB
        return context


class DatabaseDetailView(LoginRequiredMixin, DetailView):
    """Детализация базы данных."""

    model = DimDB
    template_name = 'my_dbm/databases-detail.html'
    context_object_name = 'database'


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


class TableDetailView(LoginRequiredMixin, DetailView):
    """Детализация таблицы."""

    model = LinkDBTable
    template_name = 'my_dbm/tables-detail.html'
    context_object_name = 'tables'

    def get_queryset(self):
        return LinkDBTable.objects.select_related(
            'schema', 'schema__base', 'type'
        ).prefetch_related(
            # 'linkcolumn_set__type', # неработает потом востановим
            'linkcolumn_set__linkcolumnstage_set__stage'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.object

        # Все колонки таблицы
        columns = table.linkcolumn_set.all()

        for column in columns:
            column.stages = [cs.stage for cs in column.linkcolumnstage_set.all()]

        context['column_relations'] = LinkColumnColumn.objects.filter(
            Q(main__in=columns) | Q(sub__in=columns)
        ).select_related('main', 'sub', 'type')

        # Добавляем сервисы этой таблицы
        services = LinkServicesTable.objects.filter(table=table).select_related('service')

        # Список сервисов (с их alias и type для наглядности)
        context['services_list'] = [f"{s.service.alias} ({s.service.type.name})" for s in services]
        context['services_count'] = services.count()  # Количество сервисов
        return context
