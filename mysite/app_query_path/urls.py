# app_query_path/urls.py
from django.urls import path
from .views import StartQuizView, QuestionView, ArticleView, AboutView

app_name = "app_query_path"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path("start", StartQuizView.as_view(), name="start"),
    path("question/<int:pk>/", QuestionView.as_view(), name="question"),
    path("article/<int:pk>/", ArticleView.as_view(), name="article"),
]
