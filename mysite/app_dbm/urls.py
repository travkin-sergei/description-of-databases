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
)

# API-представления (DRF)
from .views.v1 import (
    SchemaByDBAPI,
    TableBySchemaAPI,
    ColumnByTableAPI,
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
    # ——— Вспомогательные API (не через роутер) ———
    path('api/v1/schemas/by-db/', SchemaByDBAPI.as_view(), name='schemas-by-db'),
    path('api/v1/tables/by-schema/', TableBySchemaAPI.as_view(), name='tables-by-schema'),
    path('api/v1/columns/by-table/', ColumnByTableAPI.as_view(), name='columns-by-table'),

    # ——— Основной DRF API ———
    path('api/v1/', include(router.urls)),

    # ——— Веб-интерфейс (HTML) ———
    path('about/', AboutView.as_view(), name='about-app'),
    path('', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),
    path('columns/', ColumnListView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='columns-detail'),
    path('databases/', DatabasesView.as_view(), name='databases'),
]