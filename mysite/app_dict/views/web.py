# app_dict/views/web.py
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, DetailView, UpdateView, ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from ..forms import DictionaryWithSynonymsForm
from ..models import DimCategory, DimDictionary, LinkDictionaryName
from ..apps import name


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = f'app_dict/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DictionaryView(LoginRequiredMixin, ListView):
    model = DimDictionary
    template_name = f'{name}/dict.html'
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

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = DimCategory.objects.filter(is_active=True).order_by('name')
        context['title'] = _('Словари')
        return context


class DictionaryDetailView(LoginRequiredMixin, DetailView):
    """Детализация словаря."""

    model = DimDictionary
    template_name = f'{name}/dict-detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все синонимы
        context['synonyms'] = self.object.synonyms.all().order_by('synonym')
        # Дополнительные данные для контекста
        context['related_items'] = DimDictionary.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(pk=self.object.pk).order_by('name')[:5]
        context['title'] = _('Просмотр словаря: %(name)s') % {'name': self.object.name}
        return context


class DictionaryCreateView(LoginRequiredMixin, CreateView):
    """Создание словаря с синонимами"""
    model = DimDictionary
    form_class = DictionaryWithSynonymsForm
    template_name = f'{name}/dict_form.html'

    def get_success_url(self):
        messages.success(self.request, _('Словарь успешно создан'))
        return reverse_lazy(f'{name}:dict')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Создание нового словаря')
        context['action'] = 'create'
        context['synonyms'] = []  # Нет синонимов при создании
        return context


class DictionaryUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование словаря с синонимами"""
    model = DimDictionary
    form_class = DictionaryWithSynonymsForm
    template_name = f'{name}/dict-form.html'

    def get_success_url(self):
        messages.success(self.request, _('Словарь успешно обновлен'))
        return reverse_lazy(f'{name}:dict')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Редактирование словаря')
        context['action'] = 'update'
        # Получаем синонимы для текущего словаря
        context['synonyms'] = self.object.synonyms.all().order_by('synonym')
        return context
