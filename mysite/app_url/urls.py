# app_url/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.web import (
    AboutView,
    DimLinListView,
    DimLinDetailView,
)
from .views.v1 import (
    DimUrlViewSet,
)
from .apps import name

app_name = name

# Инициализация роутера для API
router = DefaultRouter()
router.register(r'api/v1/urls', DimUrlViewSet, basename='dimurl')

urlpatterns = [
    # API endpoints (через роутер DRF)
    path('', include(router.urls)),

    # WEB-интерфейс (HTML-страницы)
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('', DimLinListView.as_view(), name='dimlin_list'),
    path('link/<int:pk>/', DimLinDetailView.as_view(), name='dimlin_detail'),
]
