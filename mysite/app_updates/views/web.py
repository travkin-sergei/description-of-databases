# app_updates/views/web.py
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView

from _common.cron_processing import UniversalCronParser
from app_dbm.models import DimDB, LinkColumn

from ..forms import DimUpdateMethodForm, LinkUpdateColFormSet
from ..models import DimUpdateMethod, LinkUpdateCol
from ..filters import DimUpdateMethodFilter
import logging

logger = logging.getLogger(__name__)


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

    model = DimUpdateMethod
    template_name = 'app_updates/updates-detail.html'
    context_object_name = 'update_method'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        # Исправленный select_related - используем только существующие поля
        context['related_links'] = LinkUpdateCol.objects.filter(
            type=self.object
        ).select_related(
            'type',  # ForeignKey к DimUpdateMethod
            'main',  # ForeignKey к LinkColumn
            'main__table',  # если LinkColumn имеет ForeignKey к таблице
            'main__table__schema',  # если Table имеет ForeignKey к Schema
            'main__table__schema__base',  # если Schema имеет ForeignKey к Base
            'sub',  # ForeignKey к LinkColumn (может быть null)
            'sub__table',  # если sub не null
            'sub__table__schema',  # если sub не null
            'sub__table__schema__base'  # если sub не null
        )
        context['title'] = f"Метод обновления: {obj.name}"
        context['next_run'] = None
        context['last_run'] = None
        if obj.schedule:
            try:
                now = datetime.now()
                context['next_run'] = UniversalCronParser().get_next_execution(str(obj.schedule))
                context['last_run'] = UniversalCronParser().get_next_execution(str(obj.schedule))
            except Exception as e:
                logger.error(f"Ошибка парсинга cron '{obj.schedule}': {e}")
                context['cron_error'] = str(e)
        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()

        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()
        return context


class DimUpdateMethodAddView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """Создание расписания обновления."""

    template_name = 'app_updates/updates-add.html'
    model = DimUpdateMethod
    form_class = DimUpdateMethodForm
    success_url = reverse_lazy('app_updates:updates-list')

    # Указываем несколько разрешений (оба должны быть у пользователя)
    permission_required = [
        'app_updates.add_dimupdatemethod',  # Может добавлять методы обновления
        'app_updates.add_linkupdatecol',  # Может добавлять сопоставления столбцов
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'formset': LinkUpdateColFormSet(),
            'databases': DimDB.objects.all(),
            'title': 'Добавить метод обновления',
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        formset = LinkUpdateColFormSet(self.request.POST, instance=self.object)

        if formset.is_valid():
            formset.save()
            messages.success(self.request, 'Метод обновления успешно добавлен.')
            return response
        else:
            messages.error(self.request, 'Ошибка в сопоставлении столбцов.')
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )
