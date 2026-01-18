# app_services/view.py
from collections import defaultdict
from django_filters.views import FilterView
from django.db.models import Prefetch, Q  # <-- ДОБАВЬТЕ Q здесь
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView

from app_dbm.models import DimStage

from .filters import DimServicesFilter, DimLinkFilter
from .models import (
    DimServices,
    DimServicesName,
    DimLink, DimTechStack,
)


class PageNotFoundView(View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(TemplateView):
    """Информация о приложении."""

    template_name = 'app_services/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DimLinkListView(ListView):
    """Список ссылок."""

    model = DimLink
    filterset_class = DimLinkFilter
    template_name = 'app_services/link-list.html'
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


class ServicesView(LoginRequiredMixin, FilterView):  # Using FilterView instead of custom implementation
    """Сервисы."""

    model = DimServices
    filterset_class = DimServicesFilter
    context_object_name = 'services'
    template_name = 'app_services/services.html'
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
    template_name = 'app_services/services-detail.html'
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

        # Таблицы с пагинацией
        tables = self.object.linkservicestable_set.select_related('table').all()
        paginator = Paginator(tables, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Сортировка ссылок сначала по stack, затем по stage.pk
        links_queryset = (
            self.object.dimlink_set
            .select_related('stack', 'stage')
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
            .select_related(
                'name', 'role'
            ).filter(is_active=True)
        )

        context.update(
            {
                'tables_page_obj': page_obj,
                'paginator': paginator,
                'is_paginated': page_obj.has_other_pages(),
                'grouped_links': dict(sorted(grouped_links.items())),  # Сортировка по названию стека
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


# app_services/view.py
# app_services/view.py
class ServiceUserView(LoginRequiredMixin, ListView):
    """Отношение User к Service"""

    model = DimServices
    template_name = 'app_services/services-user.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        # Создаем копию GET параметров для очистки
        get_params = self.request.GET.copy()

        # Удаляем пустые значения из GET параметров
        for key in list(get_params.keys()):
            if get_params[key] == '':
                del get_params[key]

        # Базовый queryset
        queryset = DimServices.objects.all().prefetch_related(
            'type',
            'dimservicesname_set',
            'linkresponsibleperson_set__role',
            'linkresponsibleperson_set__name'
        ).order_by('alias')

        # Применяем фильтры с очищенными параметрами
        self.filterset = DimServicesFilter(get_params, queryset=queryset)

        # Отладочный вывод для поиска
        import sys
        print("\n" + "=" * 50, file=sys.stderr)
        print("SEARCH DEBUG:", file=sys.stderr)
        print(f"GET params: {dict(self.request.GET)}", file=sys.stderr)
        print(f"Cleaned params: {dict(get_params)}", file=sys.stderr)

        # Проверяем поисковый запрос
        search_value = get_params.get('search', '')
        print(f"Search value: '{search_value}'", file=sys.stderr)

        # Также проверяем другие параметры
        print(f"Type: {get_params.get('type', 'Не указан')}", file=sys.stderr)
        print(f"Is_active: {get_params.get('is_active', 'Не указан')}", file=sys.stderr)

        print(f"Filtered count: {self.filterset.qs.count()}", file=sys.stderr)
        print("=" * 50 + "\n", file=sys.stderr)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Используем очищенные параметры для формы
        get_params = self.request.GET.copy()
        for key in list(get_params.keys()):
            if get_params[key] == '':
                del get_params[key]

        queryset = DimServices.objects.all()
        context['filter'] = DimServicesFilter(get_params, queryset=queryset)

        # Отладочная информация
        context['debug_info'] = {
            'total_count': DimServices.objects.count(),
            'filtered_count': self.get_queryset().count(),
            'form_data': dict(get_params),
        }

        # Сохраняем параметры фильтрации для пагинации
        if get_params:
            if 'page' in get_params:
                del get_params['page']
            context['query_string'] = get_params.urlencode()

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Используем очищенные параметры для формы
        get_params = self.request.GET.copy()
        for key in list(get_params.keys()):
            if get_params[key] == '':
                del get_params[key]

        queryset = DimServices.objects.all()
        context['filter'] = DimServicesFilter(get_params, queryset=queryset)

        # Отладочная информация
        context['debug_info'] = {
            'total_count': DimServices.objects.count(),
            'filtered_count': self.get_queryset().count(),
            'form_data': dict(get_params),
            'search_test': self.test_search() if hasattr(self, 'test_search') else None,
        }

        # Сохраняем параметры фильтрации для пагинации
        if get_params:
            if 'page' in get_params:
                del get_params['page']
            context['query_string'] = get_params.urlencode()

        return context
