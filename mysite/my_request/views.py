from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from .models import FZ, ColumnFZ


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'my_request/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class FZListView(LoginRequiredMixin, ListView):
    """Столбцы подпадающие под ФЗ."""

    model = ColumnFZ
    template_name = 'my_request/fz_list.html'
    context_object_name = 'fz_list'


class FZDetailView(LoginRequiredMixin, DetailView):
    """Детализация федерального законодательства."""

    model = ColumnFZ
    template_name = 'my_request/fz_detail.html'
    context_object_name = 'fz'
