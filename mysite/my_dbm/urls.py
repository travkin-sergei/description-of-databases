from .views.web import (
    PageNotFoundView, AboutView,
    DatabasesView,  # не вижу смысла в детализации, DatabaseDetailView,
    TablesView, TableDetailView,
    ColumnListView, ColumnDetailView,

)
from django.urls import path

app_name = "my_dbm"

urlpatterns = [
    # Панель администратора

    # Миграция

    path('', AboutView.as_view(), name='about-app'),
    path('databases/', DatabasesView.as_view(), name='databases'),
    # не вижу смысла в детализации path('databases/<int:pk>/', DatabaseDetailView.as_view(), name='databases-detail'),
    path('tables/', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),
    path('columns/', ColumnListView.as_view(), name='columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='columns-detail'),
]
handler404 = PageNotFoundView.as_view()
