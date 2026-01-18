from django.urls import path

from .views.web import (
    AboutView,
    ColumnGroupListView, ColumnGroupDetailView,
    TableGroupListView,
)
from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('table-group/', TableGroupListView.as_view(), name='table-group-name'),
    # path('table-group/<int:pk>/', TableGroupDetailView.as_view(), name='table-group-name-detail'),
    path('column-group/', ColumnGroupListView.as_view(), name='column-group-name'),
    path('column-group/<int:pk>/', ColumnGroupDetailView.as_view(), name='column-group-name-detail'),
]
