from django.urls import path

from .views.views import (
    ArticleView,
    ArticleDetailView,
)

app_name = 'article'

urlpatterns = [
    path('', ArticleView.as_view(), name='home'),  # Список статей
    path('/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),  # Детали статьи
]
