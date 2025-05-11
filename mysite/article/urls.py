from django.urls import path

from .views.views import (
    about_me,
    ArticleView,
    ArticleDetailView,
)

app_name = 'article'

urlpatterns = [
    path('', ArticleView.as_view(), name='about-app'),  # о приложении
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),  # Детали статьи
]
