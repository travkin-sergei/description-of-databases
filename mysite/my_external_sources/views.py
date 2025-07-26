import json
import os
from msilib.schema import Patch

import environ
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from requests import Timeout, HTTPError, RequestException
from django.conf import settings

env = environ.Env()
environ.Env.read_env('.env')


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'my_external_sources/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class ListOfReferencesView(LoginRequiredMixin, View):
    """Представление для отображения списка ссылок из локального JSON-файла"""

    def get(self, request):

        file_path = os.path.join(settings.BASE_DIR, 'my_external_sources', 'jsonExSources', 'ListOfReferences.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)  # Читаем JSON из файла
                results = data.get('results', [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            results = []  # Обработка ошибок: файл не найден или невалидный JSON

        return render(
            request,
            'my_external_sources/ListOfReferences.html',
            {'results': results}
        )
