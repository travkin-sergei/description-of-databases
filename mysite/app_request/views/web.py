# app_request/view.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from ..filters import ColumnGroupFilter, TableGroupFilter
from ..models import ColumnGroup, TableGroup


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_request/about-app.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


# Группировка таблиц
class TableGroupListView(LoginRequiredMixin, ListView):
    """Группировка таблиц."""

    model = TableGroup
    template_name = 'app_request/table-group-name.html'
    context_object_name = 'tables'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            TableGroup.objects
            .filter(is_active=True)
            .select_related(
                'table',  # Связь с LinkColumn
                'group_name',  # Связь с TableGroupName
                'table__schema',  # Связь из LinkColumn к Schema
                'table__schema__base',  # Связь из Schema к Base
            )
            .order_by('group_name__name', 'table__name')
        )
        self.filterset = TableGroupFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs


# Группировка столбцов
class ColumnGroupListView(LoginRequiredMixin, ListView):
    """Столбцы подпадающие под ФЗ."""

    model = ColumnGroup
    template_name = 'app_request/column-group-name.html'
    context_object_name = 'columns'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            ColumnGroup.objects
            .filter(is_active=True)
            .select_related(
                'column',
                'group_name',
                'column__table__schema__base',
                'column__table__schema',
                'column__table',
            )
            .order_by('group_name__name', 'column__name')
        )
        self.filterset = ColumnGroupFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()
        else:
            context['query_string'] = ''

        return context


# Детализация столбцов
class ColumnGroupDetailView(LoginRequiredMixin, DetailView):
    """Детализация федерального законодательства."""
    model = ColumnGroup
    template_name = 'app_request/column-group-name-detail.html'  # Исправлено на правильное имя
    context_object_name = 'column_group'

    def get_queryset(self):
        return (
            ColumnGroup.objects
            .filter(is_active=True)
            .select_related(
                'column',
                'group_name',
                'column__table__schema__base',
                'column__table__schema',
                'column__table',
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Детализация: {self.object.group_name.name}"
        return context
