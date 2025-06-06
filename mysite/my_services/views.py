from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views import View
from django.views.generic import ListView

from django.http import HttpResponseNotFound
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Prefetch
from .filters import DimServicesFilter
from .models import (
    DimServices,
    DimServicesName,
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


class ServicesView(LoginRequiredMixin,ListView):
    """Сервисы."""

    model = DimServices
    filter_class = DimServicesFilter
    context_object_name = 'services'
    template_name = 'my_services/services.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related(
            Prefetch(
                'dimservicesname_set',
                queryset=DimServicesName.objects
                .all()
                .order_by('name')
            )
        )
        self.filter = self.filter_class(self.request.GET, queryset=queryset)
        return self.filter.qs.order_by('alias')


class ServicesDetailView(LoginRequiredMixin, DetailView):
    """Детализация сервисов."""

    model = DimServices
    context_object_name = 'service'
    template_name = 'my_services/services-detail.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'dimservicesname_set',
            'linkresponsibleperson_set',
            'git_services',
            'swagger_set',
            'linkservicestable_set__table'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = self.object.linkservicestable_set.select_related('table').all()

        paginator = Paginator(tables, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Получаем параметр фильтрации из URL
        stage_id = self.request.GET.get('stage_id')

        # Фильтруем Swagger по stage_id если передан
        swagger_queryset = self.object.swagger_set.all()
        if stage_id:
            swagger_queryset = swagger_queryset.filter(stage_id=stage_id)

        context.update({
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': page_obj.has_other_pages(),
            'tables_page_obj': page_obj,
            'filtered_swagger': swagger_queryset,  # Добавляем отфильтрованный queryset
            'current_stage_id': stage_id,  # Передаем текущий stage_id в контекст
        })

        return context
