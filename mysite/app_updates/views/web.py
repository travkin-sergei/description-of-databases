from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from app_dbm.models import LinkColumn
from app_dbm.models import DimDB
from ..forms import DimUpdateMethodForm, LinkUpdateColFormSet
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
    template_name = 'app_updates/updates-list.html'
    context_object_name = 'updates'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = DimUpdateMethodFilter(self.request.GET, queryset=queryset)
        filtered_qs = self.filterset.qs

        return filtered_qs.order_by('name')

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

    """Редактирование метода обновления через FormView."""
    model = DimUpdateMethod
    form_class = DimUpdateMethodForm
    template_name = 'app_updates/updates-edit.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = LinkUpdateColFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = LinkUpdateColFormSet(instance=self.object)
        context['databases'] = DimDB.objects.all()
        context['title'] = f'Редактировать: {self.object.name or "Без названия"}'
        # Явно добавляем объект для шаблона
        context['method'] = self.object
        return context
