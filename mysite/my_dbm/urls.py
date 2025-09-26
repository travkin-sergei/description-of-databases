from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.v1 import (
    DimStageViewSet,
    DimDBViewSet,
    LinkDBViewSet,
    LinkDBSchemaViewSet,
    DimDBTableTypeViewSet,
    DimColumnNameViewSet,
    LinkDBTableViewSet,
    LinkColumnViewSet,
    DimTypeLinkViewSet,
    LinkColumnColumnViewSet,
    LinkColumnNameViewSet,
    TotalDataViewSet
)
from .views.web import (
    PageNotFoundView, AboutView,
    DatabasesView, TablesView, TableDetailView,
    ColumnListView, ColumnDetailView
)

router = DefaultRouter()
# router.register(r'dim-stage', DimStageViewSet)
# router.register(r'dim-db', DimDBViewSet)
# router.register(r'link-db', LinkDBViewSet)
# router.register(r'link-db-schema', LinkDBSchemaViewSet)
# router.register(r'dim-table-type', DimDBTableTypeViewSet)
# router.register(r'dim-column-name', DimColumnNameViewSet)
# router.register(r'link-table', LinkDBTableViewSet)
# router.register(r'link-column', LinkColumnViewSet)
# router.register(r'dim-type-link', DimTypeLinkViewSet)
# router.register(r'link-column-column', LinkColumnColumnViewSet)
# router.register(r'link-column-name', LinkColumnNameViewSet)
# router.register(r'link-column-stage', LinkColumnStageViewSet)
router.register(r'total-data', TotalDataViewSet)

app_name = "my_dbm"

urlpatterns = [
    path('api/', include(router.urls)),
    path('', AboutView.as_view(), name='about-app'),
    path('databases/', DatabasesView.as_view(), name='databases'),
    path('tables/', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),
    path('columns/', ColumnListView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='columns-detail'),
]

handler404 = PageNotFoundView.as_view()