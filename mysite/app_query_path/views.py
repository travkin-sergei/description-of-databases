from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView

from .models import (
    Question,
    AnswerOption,
    Article,
)


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_query_path/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class StartQuizView(LoginRequiredMixin, View):
    """Старт квиза: редирект на первый вопрос"""

    def get(self, request, *args, **kwargs):
        first_question = Question.objects.first()
        if not first_question:
            return render(request, "app_query_path/questions_no.html")
        return redirect("app_query_path:question", pk=first_question.pk)


class QuestionView(LoginRequiredMixin, View):
    """Отображение вопроса и обработка ответа"""

    def get(self, request, pk, *args, **kwargs):
        question = get_object_or_404(Question, pk=pk)
        return render(request, "app_query_path/question.html", {"question": question})

    def post(self, request, pk, *args, **kwargs):
        question = get_object_or_404(Question, pk=pk)
        chosen_id = request.POST.get("option")
        option = get_object_or_404(AnswerOption, pk=chosen_id, question=question)

        if option.article:
            return redirect("app_query_path:article", pk=option.article.pk)
        elif option.next_question:
            return redirect("app_query_path:question", pk=option.next_question.pk)
        else:
            return render(request, "app_query_path/no_next.html", {"option": option})


class ArticleView(LoginRequiredMixin, View):
    """Отображение статьи"""

    def get(self, request, pk, *args, **kwargs):
        article = get_object_or_404(Article, pk=pk)
        return render(request, "app_query_path/article.html", {"article": article})