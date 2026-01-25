# app_url/web.py
"""
Views для приложения проверки ссылок.
Только для просмотра - без добавления/редактирования/удаления.
"""
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from ..models import DimUrl


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_dbm/about-app.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DimLinListView(LoginRequiredMixin, ListView):
    """Список всех ссылок с фильтрацией"""
    model = DimUrl
    template_name = 'app_url/dimlin_list.html'
    context_object_name = 'links'
    paginate_by = 20

    def get_queryset(self):
        """Фильтрация по статусу активности"""
        queryset = super().get_queryset().order_by('-created_at')

        # Фильтр по активности
        active_filter = self.request.GET.get('active', '').lower()
        if active_filter == 'true':
            queryset = queryset.filter(is_active=True)
        elif active_filter == 'false':
            queryset = queryset.filter(is_active=False)

        # Поиск по URL
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(url__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Добавление данных для фильтров и статистики"""
        context = super().get_context_data(**kwargs)

        # Статистика
        context['total_count'] = DimUrl.objects.count()
        context['active_count'] = DimUrl.objects.filter(is_active=True).count()
        context['inactive_count'] = DimUrl.objects.filter(is_active=False).count()

        # Параметры фильтров для сохранения в пагинации
        context['filter_params'] = self._get_filter_params()

        return context

    def _get_filter_params(self):
        """Получение параметров фильтров для пагинации"""
        params = {}
        for key in ['active', 'search']:
            value = self.request.GET.get(key, '')
            if value:
                params[key] = value
        return params


class DimLinDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о конкретной ссылке"""
    model = DimUrl
    template_name = 'app_url/dimlin_detail.html'
    context_object_name = 'link'

    def get_context_data(self, **kwargs):
        """Добавление дополнительной информации о ссылке"""
        context = super().get_context_data(**kwargs)
        link = self.object

        # Нормализованный URL для отображения
        context['normalized_url'] = DimUrl.normalize_url(link.url)

        # Похожие ссылки (с той же частотой проверки)
        if link.check_frequency:
            similar_links = DimUrl.objects.filter(
                check_frequency=link.check_frequency,
                is_active=True
            ).exclude(id=link.id)[:5]
        else:
            similar_links = DimUrl.objects.filter(
                check_frequency__isnull=True,
                is_active=True
            ).exclude(id=link.id)[:5]

        context['similar_links'] = similar_links

        return context
