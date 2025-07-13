from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from .models import DimUpdateMethod, LinkUpdate
from .filters import DimUpdateMethodFilter


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""
    template_name = 'my_updates/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DimUpdateMethodView(LoginRequiredMixin, ListView):
    """Список методов обновления."""

    model = DimUpdateMethod
    template_name = 'my_updates/updates.html'
    context_object_name = 'updates'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = DimUpdateMethodFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['title'] = "Методы обновления"
        return context


class DimUpdateMethodDetailView(LoginRequiredMixin, DetailView):
    """Детальное представление метода обновления."""

    model = DimUpdateMethod
    template_name = 'my_updates/updates-detail.html'
    context_object_name = 'update_method'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем связанные объекты LinkUpdate с предварительной выборкой
        context['related_links'] = LinkUpdate.objects.filter(
            name=self.object
        ).select_related(
            'column__main__table__schema__base',
            'column__main__table__schema',
            'column__main__table',
            'column__main',
            'column__sub__table__schema__base',
            'column__sub__table__schema',
            'column__sub__table',
            'column__sub',
            'column__type'
        )
        context['title'] = f"Метод обновления: {self.object.name}"
        return context