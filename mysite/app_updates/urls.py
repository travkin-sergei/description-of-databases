# app_updates/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.v1 import DimUpdateMethodViewSet, LinkUpdateColViewSet
from .views.web import (
    AboutView,
    DimUpdateMethodDetailView, DimUpdateMethodView,
)
from .apps import AppUpdatesConfig  # Исправлен импорт

# Пространство имён приложения
app_name = AppUpdatesConfig.name

# Роутер для API версии 1
api_router = DefaultRouter()
api_router.register(r'updates', DimUpdateMethodViewSet, basename='updates')
api_router.register(r'update-columns', LinkUpdateColViewSet, basename='update-column')  # Единственное число

# Основные URL-паттерны приложения
urlpatterns = [
    # API
    path('api/v1/', include(api_router.urls)),
    # web
    path('about/', AboutView.as_view(), name='about-app'),
    path('updates/', DimUpdateMethodView.as_view(), name='updates'),
    path('updates/<int:pk>/', DimUpdateMethodDetailView.as_view(), name='updates-detail'),
]
