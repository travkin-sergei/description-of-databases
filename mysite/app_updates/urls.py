# app_updates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.v1 import DimUpdateMethodViewSet, LinkUpdateColViewSet
from .views.web import (
    AboutView,
    DimUpdateMethodView,
    DimUpdateMethodDetailView,
)
from .apps import name

app_name = name

router = DefaultRouter()
router.register(r'api/v1/update-methods', DimUpdateMethodViewSet, basename='update-method')
router.register(r'api/v1/update-columns', LinkUpdateColViewSet, basename='update-columns')

urlpatterns = [
    # API v1
    path('', include(router.urls)),
    # WEB страницы
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('updates/', DimUpdateMethodView.as_view(), name='updates'),
    path('updates/<int:pk>/', DimUpdateMethodDetailView.as_view(), name='updates-detail'),

    # API документация (опционально)
    path('api-auth/', include('rest_framework.urls')),
]