# app_updates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_dbm.views.web import (
    GetSchemasView,
    GetTablesView,
    GetColumnsView,
)
from .views.v1 import DimUpdateMethodViewSet, LinkUpdateColViewSet
from .views.web import (
    AboutView,
    DimUpdateMethodDetailView,
    DimUpdateMethodView,
)
from .views.web_form_update import (
    DimUpdateMethodAddView,  # Добавление данных
    DimUpdateMethodUpdateView, DimUpdateMethodDeleteView,  # Обновление данных
)

from .apps import AppUpdatesConfig

app_name = AppUpdatesConfig.name

api_router = DefaultRouter()
api_router.register(r'updates', DimUpdateMethodViewSet, basename='updates')
api_router.register(r'update-columns', LinkUpdateColViewSet, basename='update-column')

urlpatterns = [
    # API
    path('api/schemas/', GetSchemasView.as_view(), name='get-schemas'),
    path('api/tables/', GetTablesView.as_view(), name='get-tables'),
    path('api/columns/', GetColumnsView.as_view(), name='get-columns'),
    path('api/v1/', include(api_router.urls)),
    # WEB
    path('about/', AboutView.as_view(), name='about-app'),
    path('', DimUpdateMethodView.as_view(), name='updates-list'),
    path('<int:pk>/', DimUpdateMethodDetailView.as_view(), name='updates-detail'),
    path('add/', DimUpdateMethodAddView.as_view(), name='updates-add'),
    path('<int:pk>/edit/', DimUpdateMethodUpdateView.as_view(), name='updates-edit'),
    path('<int:pk>/delete/', DimUpdateMethodDeleteView.as_view(), name='updates-delete'),
]
