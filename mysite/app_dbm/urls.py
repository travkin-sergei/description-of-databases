# app_dbm/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.web import (
    AboutView, DatabasesView, TablesView,
    TableDetailView, ColumnListView, ColumnDetailView,
    SchemaAPIView, TableAPIView, ColumnAPIView, LinkColumnColumnCreateView
)
from .views.v1 import (
    SchemaByDBAPI, TableBySchemaAPI, ColumnByTableAPI,
    DimStageViewSet, DimDBViewSet, LinkDBViewSet,
    DimColumnNameViewSet, LinkColumnViewSet,
    DimTypeLinkViewSet, LinkColumnColumnViewSet,
    LinkColumnNameViewSet, TotalDataViewSet
)

router = DefaultRouter()
router.register(r'dim-stage', DimStageViewSet, basename='dim-stage')

app_name = 'dbm'

urlpatterns = [
    # API маршруты
    path('api/v1/', include(router.urls)),
    # Веб-маршруты - ВСЕ с правильными именами
    path('about/', AboutView.as_view(), name='about-app'),
    path('', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),
    path('columns/', ColumnListView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='columns-detail'),
    path('databases/', DatabasesView.as_view(), name='databases'),
]
# 404 ошибка обрабатывается на уровне приложения