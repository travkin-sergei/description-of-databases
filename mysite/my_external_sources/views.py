import json
import os

import environ
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from requests import Timeout, HTTPError, RequestException

env = environ.Env()
environ.Env.read_env('.env')


class PageNotFoundView(LoginRequiredMixin,View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin,TemplateView):
    """Страница о приложении."""

    template_name = 'my_external_sources/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class ListOfReferencesView(LoginRequiredMixin,View):
    """Представление для отображения списка ссылок из локального JSON-файла"""

    def get(self, request):
        file_path = os.path.join(
            os.path.dirname(__file__), 'jsonExSources', 'ListofReferences.f.json'
        )

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



class EcomruEntities(LoginRequiredMixin,View):
    def get(self, request):
        params = {
            "accept": "application/f.json",
            "Authorization": f"Bearer {env('ECOMRU_KEY')}"  # Используем settings
        }
        url = "https://appche3.ecomru.ru:4448/api/v1/entities"

        try:
            # Устанавливаем таймауты (соединение и чтение в секундах)
            response = requests.get(url, headers=params, timeout=(5, 10))
            response.raise_for_status()  # Вызовет исключение для 4XX/5XX статусов

            try:
                results = response.json()
            except ValueError:
                results = []
                print("Ошибка: не удалось декодировать JSON ответ")

        except Timeout:
            results = []
            print("Ошибка: время ожидания соединения истекло")
        except ConnectionError:
            results = []
            print("Ошибка: не удалось установить соединение")
        except HTTPError as http_err:
            results = []
            print(f"HTTP ошибка: {http_err}")
        except RequestException as req_err:
            results = []
            print(f"Ошибка запроса: {req_err}")
        except Exception as e:
            results = []
            print(f"Неожиданная ошибка: {e}")

        return render(
            request,
            'my_external_sources/EcomruEntities.html',
            {'results': results, 'error': bool(not results)}
        )