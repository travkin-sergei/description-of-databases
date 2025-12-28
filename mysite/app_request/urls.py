from django.urls import path

from .views import (
    AboutView, PageNotFoundView,
    ColumnGroupListView, ColumnGroupDetailView,
    TableGroupListView, TableGroupDetailView,
)

app_name = "app_request"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('column-group/', ColumnGroupListView.as_view(), name='column-group-name'),
    path('column-group/<int:pk>/', ColumnGroupDetailView.as_view(), name='column-group-name-detail'),
    path('table-group/', TableGroupListView.as_view(), name='table-group-name'),
    path('table-group/<int:pk>/', TableGroupDetailView.as_view(), name='table-group-name-detail'),
]
handler404 = PageNotFoundView.as_view()
