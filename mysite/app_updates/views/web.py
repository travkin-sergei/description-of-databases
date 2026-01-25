from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from ..models import DimUpdateMethod, LinkUpdateCol
from ..filters import DimUpdateMethodFilter


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""
    template_name = 'app_updates/about-app.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DimUpdateMethodView(LoginRequiredMixin, ListView):
    """Список методов обновления."""

    model = DimUpdateMethod
    template_name = 'app_updates/updates.html'
    context_object_name = 'updates'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Используйте DimUpdateMethodFilter вместо LinkUpdateColAdminForm
        self.filterset = DimUpdateMethodFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['title'] = "Методы обновления"
        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()
        return context


class DimUpdateMethodDetailView(LoginRequiredMixin, DetailView):
    """Детальное представление метода обновления."""

    model = DimUpdateMethod
    template_name = 'app_updates/updates-detail.html'
    context_object_name = 'update_method'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Исправленный select_related - используем только существующие поля
        context['related_links'] = LinkUpdateCol.objects.filter(
            type=self.object
        ).select_related(
            'type',                      # ForeignKey к DimUpdateMethod
            'main',                      # ForeignKey к LinkColumn
            'main__table',               # если LinkColumn имеет ForeignKey к таблице
            'main__table__schema',       # если Table имеет ForeignKey к Schema
            'main__table__schema__base', # если Schema имеет ForeignKey к Base
            'sub',                       # ForeignKey к LinkColumn (может быть null)
            'sub__table',                # если sub не null
            'sub__table__schema',        # если sub не null
            'sub__table__schema__base'   # если sub не null
        )
        context['title'] = f"Метод обновления: {self.object.name}"

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()
        return context