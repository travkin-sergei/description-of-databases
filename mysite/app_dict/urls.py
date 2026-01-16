# app_dict/urls.py
from django.urls import path
from .views.web import (
    AboutView,
    DictionaryView, DictionaryDetailView,
)
from .apps import name

app_name = name

urlpatterns = [
    path('about/', AboutView.as_view(), name='about-app'),
    path('', DictionaryView.as_view(), name='dict'),
    path('<int:pk>/', DictionaryDetailView.as_view(), name='dict-detail'),
]
