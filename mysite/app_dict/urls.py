# app_dict/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.v1 import CategoryViewSet, DictionaryViewSet
from .views.web import (
    AboutView,
    DictionaryView, DictionaryDetailView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'dictionary', DictionaryViewSet, basename='dictionary')
from .apps import name

app_name = name

urlpatterns = [
    # API
    path('v1/', include(router.urls)),
    # web
    path('about/', AboutView.as_view(), name='about-app'),
    path('', DictionaryView.as_view(), name='dict'),
    path('<int:pk>/', DictionaryDetailView.as_view(), name='dict-detail'),
]
