# app_request/view.py
from django.http import HttpResponseNotFound
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .filters import ColumnGroupFilter
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from .models import ColumnGroup


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


class ColumnGroupListView(LoginRequiredMixin, ListView):
    """Столбцы подпадающие под ФЗ."""

    model = ColumnGroup
    template_name = 'app_request/group_name.html'
    context_object_name = 'fz_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(is_active=True)
            .select_related(
                'column',
                'column__table__schema__base',
                'column__table__schema',
                'column__table',
            )
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

        return context


class ColumnGroupDetailView(LoginRequiredMixin, DetailView):
    """Детализация федерального законодательства."""

    model = ColumnGroup
    template_name = 'app_request/column_group-detail.html'
    context_object_name = 'column_group'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_active=True)
            .select_related(
                'column_group',
                'column__table__schema__base',
                'column__table__schema',
                'column__table',
            )
        )
