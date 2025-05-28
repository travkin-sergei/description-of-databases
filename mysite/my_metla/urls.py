# urls.py
from django.urls import path

from .view.web import (
    my_metla_view,
    AboutAppView,
    BaseListView,
    SchemaTablesView,
)

app_name = 'my_metla'

urlpatterns = [
    path('metla/', my_metla_view, name='my-metla'),  # тестовая страница
    path('', AboutAppView.as_view(), name='about-app'),
    path('databases/', BaseListView.as_view(), name='database-list'),
    path('schemas/tables/', SchemaTablesView.as_view(), name='schema-tables-list'),
    # path('schemas/<int:base_id>/tables/', SchemaTablesView.as_view(), name='schema-tables'),
    # # path('schemas/', BaseSchemaListView.as_view(), name='base-schema-list'),
    # # path('base-schema-tables/', SchemaTableListView.as_view(), name='schema-tables'),
    # path('table/<int:pk>/', TableDetailView.as_view(), name='table-detail'),
]
