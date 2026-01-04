# app_dbm/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.ajax import linked_form_view, get_schemas, get_tables, get_columns
from .views.web import (
    PageNotFoundView, AboutView,
    DatabasesView,
    TablesView,
    TableDetailView,
    ColumnListView,
    ColumnDetailView, LinkColumnColumnCreateView
)
from .views.v1 import (
    # DimStageViewSet,
    # DimDBViewSet,
    # LinkDBViewSet,
    # LinkSchemaViewSet,
    # DimTableTypeViewSet,
    # DimColumnNameViewSet,
    # LinkTableViewSet,
    # LinkColumnViewSet,
    # DimTypeLinkViewSet,
    # LinkColumnColumnViewSet,
    # LinkColumnNameViewSet,
    TotalDataViewSet
)

app_name = 'app_dbm'

router = DefaultRouter()
router.register(r'total-data', TotalDataViewSet),

urlpatterns = [
    # API
    path('api/', include(router.urls)),
    path('api/link-column-column/create/', LinkColumnColumnCreateView.as_view(), name='link_column_column_create'),
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('', DatabasesView.as_view(), name='databases'),
    path('tables/', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),
    path('columns/', ColumnListView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='columns-detail'),
    # ajax.py
    path('linked-form/', linked_form_view, name='linked_form'),
    path('get-schemas/', get_schemas, name='get_schemas'),
    path('get-tables/', get_tables, name='get_tables'),
    path('get-columns/', get_columns, name='get_columns'),
]
handler404 = PageNotFoundView.as_view()
