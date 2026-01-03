# app_services/views/web.py
from collections import defaultdict

from django.utils import timezone
from django_filters.views import FilterView
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView

from app_dbm.models import DimStage, LinkTable

from ..filters import DimServicesFilter, LinksUrlServiceFilter
from ..models import (
    DimServices,
    DimServicesName,
    DimServicesTypes,
    DimRoles,
    DimTechStack,
    LinksUrlService,
    LinkServicesServices,
    LinkResponsiblePerson,
    LinkServicesTable,
    DimServicesNameType,
)


class PageNotFoundView(View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(TemplateView):
    template_name = 'app_services/about-application.html'
    title = "О модуле Управление сервисами"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['current_year'] = timezone.now().year
        context['version'] = '1.0.0'

        return context


class LinksUrlServiceListView(ListView):
    """Список ссылок сервисов."""

    model = LinksUrlService
    filterset_class = LinksUrlServiceFilter
    template_name = 'app_services/link-list.html'
    context_object_name = 'links'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'url', 'service', 'stack', 'stage'
        )
        self.filter = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filter.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        # Добавляем querysets для фильтров
        context['tech_stacks'] = DimTechStack.objects.all()
        context['stages'] = DimStage.objects.all()
        context['services'] = DimServices.objects.all()

        return context


class ServicesView(LoginRequiredMixin, FilterView):
    """Список сервисов."""

    model = DimServices
    filterset_class = DimServicesFilter
    context_object_name = 'services'
    template_name = 'app_services/services.html'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('type').prefetch_related(
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

        # Добавляем типы сервисов для фильтра
        context['service_types'] = DimServicesTypes.objects.all()
        context['roles'] = DimRoles.objects.all()

        return context


class ServicesDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о сервисе."""

    model = DimServices
    context_object_name = 'service'
    template_name = 'app_services/services-detail.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related('type').prefetch_related(
            'dimservicesname_set',
            Prefetch(
                'linkresponsibleperson_set',
                queryset=LinkResponsiblePerson.objects.select_related('name__user', 'role').filter(is_active=True)
            ),
            Prefetch(
                'linkservicestable_set',
                queryset=LinkServicesTable.objects.select_related('table').filter(is_active=True)
            ),
            Prefetch(
                'linksurlservice_set',
                queryset=LinksUrlService.objects.select_related('url', 'stack', 'stage').filter(is_active=True)
            ),
            Prefetch(
                'my_main',
                queryset=LinkServicesServices.objects.select_related('sub', 'sub__type').filter(is_active=True)
            ),
            Prefetch(
                'my_sub',
                queryset=LinkServicesServices.objects.select_related('main', 'main__type').filter(is_active=True)
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Таблицы с пагинацией
        tables = self.object.linkservicestable_set.select_related('table').filter(is_active=True)
        paginator = Paginator(tables, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Сортировка ссылок сервисов сначала по stack, затем по stage.pk
        links_queryset = (
            self.object.linksurlservice_set
            .select_related('stack', 'stage', 'url')
            .filter(is_active=True)
            .order_by('stack__name', 'stage__pk', 'link_name')
        )

        # Группировка отсортированных ссылок по технологии
        grouped_links = defaultdict(list)
        for link in links_queryset:
            key = link.stack.name if link.stack else "Без технологии"
            grouped_links[key].append(link)

        # Дополнительная сортировка внутри каждой группы по stage.pk
        for stack_name in grouped_links:
            grouped_links[stack_name].sort(key=lambda x: (x.stage.pk if x.stage else 0, x.link_name))

        # Остальные данные
        as_main = self.object.my_main.filter(is_active=True).select_related('sub')
        as_sub = self.object.my_sub.filter(is_active=True).select_related('main')
        responsible_persons = (
            self.object
            .linkresponsibleperson_set
            .select_related('name__user', 'role')
            .filter(is_active=True)
        )

        context.update(
            {
                'tables_page_obj': page_obj,
                'paginator': paginator,
                'is_paginated': page_obj.has_other_pages(),
                'grouped_links': dict(sorted(grouped_links.items())),
                'as_main': as_main,
                'as_sub': as_sub,
                'responsible_persons': responsible_persons,
                'all_names': self.object.all_names,
            }
        )

        # Сохраняем параметры для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        return context


class ServiceUserView(LoginRequiredMixin, FilterView):
    """Сервисы, связанные с пользователем."""

    model = DimServices
    filterset_class = DimServicesFilter
    template_name = 'app_services/services-user.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('type').prefetch_related(
            'dimservicesname_set',
            Prefetch(
                'linkresponsibleperson_set',
                queryset=LinkResponsiblePerson.objects.select_related('role', 'name__user')
            ),
        ).order_by('alias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отладочная информация
        context['debug_info'] = {
            'total_count': DimServices.objects.count(),
            'filtered_count': self.object_list.count(),
            'form_data': dict(self.request.GET),
        }

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        return context