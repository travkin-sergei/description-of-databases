from django.urls import path

from .views.views import (
    about_me,
    ArticleView,
    ArticleDetailView,
)

app_name = 'article'

urlpatterns = [
    path('about-me/', about_me, name='about_me'),
    path('', ArticleView.as_view(), name='home'),  # Список статей
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),  # Детали статьи
]
