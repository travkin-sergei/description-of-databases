# app_request/view.py
from django.http import HttpResponseNotFound
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from .filters import ColumnGroupFilter
from .models import ColumnGroup, TableGroup


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_request/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


# Группировка таблиц
class TableGroupListView(LoginRequiredMixin, ListView):
    """Столбцы подпадающие под ФЗ."""

    model = ColumnGroup
    template_name = 'app_request/column-group-name.html'
    context_object_name = 'fz_list'
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


class TableGroupDetailView(LoginRequiredMixin, DetailView):
    """Детализация федерального законодательства."""
    model = TableGroup
    template_name = 'app_request/table-group-name-detail.html'  # Исправлено на правильное имя
    context_object_name = 'table_group'

    def get_queryset(self):
        return (
            ColumnGroup.objects
            .filter(is_active=True)
            .select_related(
                'group_name',
                'table__schema__base',
                'table__schema',
                'table',
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Детализация: {self.object.group_name.name}"
        return context


# Группировка столбцов
class ColumnGroupListView(LoginRequiredMixin, ListView):
    """Столбцы подпадающие под ФЗ."""

    model = ColumnGroup
    template_name = 'app_request/column-group-name.html'
    context_object_name = 'fz_list'
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
