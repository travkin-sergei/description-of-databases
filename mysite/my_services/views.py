from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import ListView

from django.http import HttpResponseNotFound
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Prefetch
from django_filters.views import FilterMixin, FilterView

from .filters import DimServicesFilter
from .models import (
    DimServices,
    DimServicesName, LinkServicesServices,
)


class PageNotFoundView(View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(TemplateView):
    """Информация о приложении."""

    template_name = 'my_services/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class ServicesView(LoginRequiredMixin, FilterView):  # Using FilterView instead of custom implementation
    """Сервисы."""

    model = DimServices
    filterset_class = DimServicesFilter
    context_object_name = 'services'
    template_name = 'my_services/services.html'
    paginate_by = 20

    def get_queryset(self):
        # Get the base queryset from FilterView
        queryset = super().get_queryset()

        # Apply your custom prefetch
        queryset = queryset.prefetch_related(
            Prefetch(
                'dimservicesname_set',
                queryset=DimServicesName.objects.all().order_by('name')
            )
        )
        return queryset.order_by('alias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        return context


class ServicesDetailView(LoginRequiredMixin, DetailView):
    """Детализация сервисов."""

    model = DimServices
    context_object_name = 'service'
    template_name = 'my_services/services-detail.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'dimservicesname_set',  # Синонимы сервиса
            'linkresponsibleperson_set__name',  # Ответственные лица с профилями
            'linkresponsibleperson_set__role',  # Ответственные лица с ролями
            'linkservicestable_set__table',  # Таблицы сервиса
            'linklink_set__link',  # Ссылки на репозитории
            'linklink_set__stage',  # Стадии для ссылок
            # Связи между сервисами
            'my_main__sub',  # Где текущий сервис главный
            'my_sub__main'   # Где текущий сервис подчиненный
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Пагинация для таблиц
        tables = self.object.linkservicestable_set.select_related('table').all()
        paginator = Paginator(tables, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Фильтрация ссылок по stage_id
        stage_id = self.request.GET.get('stage_id')
        links_queryset = self.object.linklink_set.select_related('link', 'stage').filter(is_active=True)
        if stage_id:
            links_queryset = links_queryset.filter(stage_id=stage_id)

        # Получаем связанные сервисы
        as_main = self.object.my_main.all().select_related('sub')
        as_sub = self.object.my_sub.all().select_related('main')

        # Ответственные лица с дополнительной информацией
        responsible_persons = self.object.linkresponsibleperson_set.select_related(
            'name', 'role'
        ).filter(is_active=True)

        context.update({
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': page_obj.has_other_pages(),
            'tables_page_obj': page_obj,
            'links': links_queryset,  # Переименовано с swagger на links
            'current_stage_id': stage_id,
            'as_main': as_main,
            'as_sub': as_sub,
            'responsible_persons': responsible_persons,
            'all_names': self.object.all_names,  # Используем property из модели
        })
        return context
