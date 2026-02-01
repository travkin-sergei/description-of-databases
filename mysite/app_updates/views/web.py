# app_updates/views/web.py
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect
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


# app_updates/views/web.py
class DimUpdateMethodAddView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """Создание расписания обновления."""

    template_name = 'app_updates/updates-add.html'
    model = DimUpdateMethod
    form_class = DimUpdateMethodForm
    success_url = reverse_lazy('app_updates:updates-list')

    permission_required = [
        'app_updates.add_dimupdatemethod',
        'app_updates.add_linkupdatecol',
    ]

    def get_formset(self, instance=None):
        """Создание или получение formset."""
        if self.request.method == 'POST':
            return LinkUpdateColFormSet(
                self.request.POST,
                self.request.FILES,
                instance=instance
            )
        return LinkUpdateColFormSet(instance=instance)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем formset с правильным instance
        formset = self.get_formset(instance=self.object)

        # Добавляем все необходимые данные в контекст
        context.update({
            'formset': formset,
            'databases': DimDB.objects.all().only('id', 'name'),
            'title': 'Добавить метод обновления',
            'help_text': {
                'schedule': 'Формат cron: минутa час день месяц день_недели',
                'columns': 'Выберите основную и дополнительную колонки для обновления'
            }
        })

        # Для отладки - логируем количество форм
        logger.debug(f"Formset created with {formset.total_form_count} forms")

        return context

    def form_valid(self, form):
        """Обработка валидной формы."""
        try:
            # Сохраняем основной объект без коммита
            self.object = form.save(commit=False)
            self.object.save()  # Теперь сохраняем

            # Создаем formset с instance
            formset = self.get_formset(instance=self.object)

            if formset.is_valid():
                formset.save()
                messages.success(
                    self.request,
                    f'Метод обновления "{self.object.name}" успешно создан.'
                )
                return HttpResponseRedirect(self.get_success_url())
            else:
                # Если formset невалиден, показываем ошибки
                for error in formset.non_form_errors():
                    messages.error(self.request, error)
                for form_in_formset in formset:
                    for field, errors in form_in_formset.errors.items():
                        for error in errors:
                            messages.error(self.request, f"Строка {form_in_formset.prefix}: {error}")
                return self.render_to_response(
                    self.get_context_data(form=form, formset=formset)
                )

        except Exception as e:
            logger.error(f"Ошибка при создании метода обновления: {e}")
            messages.error(
                self.request,
                f'Произошла ошибка при сохранении: {str(e)}'
            )
            return self.render_to_response(
                self.get_context_data(form=form, formset=self.get_formset())
            )

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса."""
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
