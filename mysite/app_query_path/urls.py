# app_query_path/urls.py

from django.urls import path
from .apps import AppQueryPathConfig

# web
from .views.web import (
    AboutView,
    StartQuizView,
    QuestionView,
    ArticleView,
)

# API
from .views.v1 import (
    StartQuestionAPIView,
    NextStepAPIView,
    QuestionListView,
    ArticleListView
)

app_name = AppQueryPathConfig.name

urlpatterns = [
    # === API (v1) ===
    path('api/v1/start/', StartQuestionAPIView.as_view(), name='start-question'),
    path('api/v1/next/', NextStepAPIView.as_view(), name='next-step'),
    path('api/v1/questions/', QuestionListView.as_view(), name='questions-list'),
    path('api/v1/articles/', ArticleListView.as_view(), name='articles-list'),

    # === Веб-интерфейс ===
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('start/', StartQuizView.as_view(), name='start_quiz'),
    path('question/<int:pk>/', QuestionView.as_view(), name='question'),
    path('article/<int:pk>/', ArticleView.as_view(), name='article'),
]
