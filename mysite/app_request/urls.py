# app_request/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.v1 import (
    TableGroupNameViewSet,
    TableGroupViewSet,
    ColumnGroupNameViewSet,
    ColumnGroupViewSet
)
from .views.web import (
    AboutView,
    ColumnGroupListView,
    ColumnGroupDetailView,
    TableGroupListView,
)
from .apps import AppRequestConfig

# Пространство имён приложения
app_name = AppRequestConfig.name

# === API Router ===
router = DefaultRouter()
router.register(r'table-group-names', TableGroupNameViewSet, basename='table-group-name')
router.register(r'table-groups', TableGroupViewSet, basename='table-group')
router.register(r'column-group-names', ColumnGroupNameViewSet, basename='column-group-name')
router.register(r'column-groups', ColumnGroupViewSet, basename='column-group')

# === URL-маршруты ===
urlpatterns = [
    # API v1
    path('api/v1/', include(router.urls)),

    # Web-страницы
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('table-group/', TableGroupListView.as_view(), name='table-group-name'),
    path('column-group/', ColumnGroupListView.as_view(), name='column-group-name'),
    path('column-group/<int:pk>/', ColumnGroupDetailView.as_view(), name='column-group-detail'),
]
