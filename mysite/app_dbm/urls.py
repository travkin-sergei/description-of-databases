# app_dbm/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Веб-представления (HTML)
from .views.web import (
    AboutView,
    DatabasesView,
    TablesView,
    TableDetailView,
    ColumnListView,
    ColumnDetailView,
    GetSchemasView,
    GetTablesView,
    GetColumnsView,
)

# API-представления (DRF)
from .views.v1 import (
    DimStageViewSet,
    DimDBViewSet,
    LinkDBViewSet,
    DimColumnNameViewSet,
    LinkColumnViewSet,
    DimTypeLinkViewSet,
    LinkColumnColumnViewSet,
    LinkColumnNameViewSet,
    TotalDataViewSet,
)

from .apps import AppDbmConfig

app_name = AppDbmConfig.name

# === DRF Router ===
router = DefaultRouter()
router.register(r'dim-stage', DimStageViewSet, basename='dim-stage')
router.register(r'dim-db', DimDBViewSet, basename='dim-db')
router.register(r'link-db', LinkDBViewSet, basename='link-db')
router.register(r'dim-column-name', DimColumnNameViewSet, basename='dim-column-name')
router.register(r'link-column', LinkColumnViewSet, basename='link-column')
router.register(r'dim-type-link', DimTypeLinkViewSet, basename='dim-type-link')
router.register(r'link-column-column', LinkColumnColumnViewSet, basename='link-column-column')
router.register(r'link-column-name', LinkColumnNameViewSet, basename='link-column-name')
router.register(r'total-data', TotalDataViewSet, basename='total-data')

# === URL Patterns ===
urlpatterns = [

    # DRF AP
    path('api/v1/', include(router.urls)),
    # Для AJAX
    path('api/schemas/', GetSchemasView.as_view(), name='get-schemas'),
    path('api/tables/', GetTablesView.as_view(), name='get-tables'),
    path('api/columns/', GetColumnsView.as_view(), name='get-columns'),
    # HTML)
    path('about/', AboutView.as_view(), name='about-app'),
    path('', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),
    path('columns/', ColumnListView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='columns-detail'),
    path('databases/', DatabasesView.as_view(), name='databases'),
]
