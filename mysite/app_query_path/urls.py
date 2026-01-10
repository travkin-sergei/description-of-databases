# app_query_path/urls.py
from django.urls import path

from .views.web import AboutView, StartQuizView, QuestionView, ArticleView
from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('start/', StartQuizView.as_view(), name='start_quiz'),
    path('question/<int:pk>/', QuestionView.as_view(), name='question'),
    path('article/<int:pk>/', ArticleView.as_view(), name='article'),
]
