from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView,
)

from .models import LinkUpdate, LinkColumnUpdate


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'my_updates/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class LinkColumnUpdateView(ListView):
    model = LinkColumnUpdate
    template_name = 'my_updates/updates.html'
    context_object_name = 'updates'
    paginate_by = 20
