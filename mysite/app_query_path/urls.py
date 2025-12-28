# app_query_path/urls.py
from django.urls import path
from . import views

app_name = 'app_query_path'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('start/', views.StartQuizView.as_view(), name='start_quiz'),
    path('question/<int:pk>/', views.QuestionView.as_view(), name='question'),
    path('article/<int:pk>/', views.ArticleView.as_view(), name='article'),
]