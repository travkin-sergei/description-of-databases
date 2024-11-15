from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from ..filters import ArticleFilter
from ..models import Article


def about_me(request):
    """
    Отображение информации о текущем приложении из шалона.
    """
    return render(request, 'article/about_application.html')


class FilteredListView(ListView, LoginRequiredMixin):
    """
    Класс фильтрации данных.
    Необходим для сокращения кода объектов класса ListView т.к. имеется пагинация
    """
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context


class ArticleView(FilteredListView, LoginRequiredMixin):
    """
    Список Статей
    """
    template_name = 'article/Article.html'
    model = Article
    filter_class = ArticleFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем текущие параметры GET
        query_dict = self.request.GET.copy()
        # Удаляем параметр 'page'
        query_dict.pop('page', None)
        context['query_params'] = query_dict.urlencode()  # Передаем строку запроса в контекст
        return context


class ArticleDetailView(DetailView, LoginRequiredMixin):
    """
    Описание статей
    """
    model = Article
    template_name = 'article/a-bout.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
