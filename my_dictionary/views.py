from django.http import HttpResponseNotFound
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from .models import DimCategory, DimDictionary


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'my_dictionary/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DictionaryView(LoginRequiredMixin,ListView):
    model = DimDictionary
    template_name = 'my_dictionary/dictionary.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.GET

        # Поиск по name (DimDictionary) и synonym (LinkDictionaryName)
        if search_query := params.get('name'):
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(synonyms__synonym__icontains=search_query)
            ).distinct()  # Убираем дубликаты

        if category_id := params.get('category'):
            queryset = queryset.filter(category_id=category_id)

        if description := params.get('description'):
            queryset = queryset.filter(description__icontains=description)

        if is_active := params.get('is_active'):
            queryset = queryset.filter(is_active=(is_active == 'true'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = DimCategory.objects.filter(is_active=True)
        return context


class DictionaryDetailView(LoginRequiredMixin,DetailView):
    """Детализация словаря."""

    model = DimDictionary
    template_name = 'my_dictionary/dictionary-detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Дополнительные данные для контекста
        context['related_items'] = DimDictionary.objects.filter(
            category=self.object.category
        ).exclude(pk=self.object.pk)[:5]
        return context