# urls.py
from django.urls import path

from .view.web import (
    AboutAppView, BaseListView, my_metla_view,
    BaseSchemaListView,
    SchemaTableListView,
    TableDetailView,
)

app_name = 'my_metla'

urlpatterns = [
    path('', AboutAppView.as_view(), name='about-app'),
    path('databases/', BaseListView.as_view(), name='database-list'),
    path('metla/', my_metla_view, name='my_metla'),
    path('schemas/', BaseSchemaListView.as_view(), name='base-schema-list'),
    path('base-schema-tables/', SchemaTableListView.as_view(), name='schema-tables'),
    path('table/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
]
