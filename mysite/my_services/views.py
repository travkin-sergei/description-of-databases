from collections import defaultdict
from django_filters.views import FilterView
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView

from .filters import DimServicesFilter, DimLinkFilter
from my_dbm.models import DimStage
from .models import (
    DimServices,
    DimServicesName,
    DimLink,
    DimTechStack,
    LinkResponsiblePerson,
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
        queryset = super().get_queryset()
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
    model = DimServices
    context_object_name = 'service'
    template_name = 'my_services/services-detail.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'dimservicesname_set',
            'linkresponsibleperson_set__name',
            'linkresponsibleperson_set__role',
            'linkservicestable_set__table',
            'dimlink_set__stack',
            'dimlink_set__stage',
            'my_main__sub',
            'my_sub__main',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tables = self.object.linkservicestable_set.select_related('table').all()
        paginator = Paginator(tables, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        links_queryset = self.object.dimlink_set.select_related('stack', 'stage').filter(is_active=True)

        # 🔸 Группировка ссылок по технологии
        grouped_links = defaultdict(list)
        for link in links_queryset:
            key = link.stack.name if link.stack else "Без технологии"
            grouped_links[key].append(link)

        as_main = self.object.my_main.all().select_related('sub')
        as_sub = self.object.my_sub.all().select_related('main')

        responsible_persons = self.object.linkresponsibleperson_set.select_related(
            'name', 'role'
        ).filter(is_active=True)

        context.update({
            'tables_page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': page_obj.has_other_pages(),
            'grouped_links': dict(grouped_links),
            'as_main': as_main,
            'as_sub': as_sub,
            'responsible_persons': responsible_persons,
            'all_names': self.object.all_names,
        })
        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()
        return context


class DimLinkListView(ListView):
    """Список ссылок."""

    model = DimLink
    filterset_class = DimLinkFilter
    template_name = 'my_services/link-list.html'
    context_object_name = 'links'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
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
        context['stages'] = DimStage.objects.all()  # Опечатка в оригинале (stages вместо stages)
        return context
