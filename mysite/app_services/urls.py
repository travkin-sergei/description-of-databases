# app_services/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.graph import ServiceGraphView, ServiceGraphDataView
from .views.web import (
    AboutView,
    ServicesView,
    ServicesDetailView,
    LinksUrlServiceListView,
    ServiceUserView,
)
from .views.v1 import (
    DimServicesViewSet,
    DimServicesTypesViewSet,
    DimServicesNameViewSet,
    DimRolesViewSet,
    LinkResponsiblePersonViewSet,
    LinksUrlServiceViewSet,
    DimStackViewSet,
    LinkDocViewSet,
)
from .apps import name

app_name = name

# Инициализация роутера DRF
router = DefaultRouter()

# Регистрация ViewSet с понятными basename
router.register(r'services-types', DimServicesTypesViewSet, basename='services-types')
router.register(r'services', DimServicesViewSet, basename='services')
router.register(r'services-names', DimServicesNameViewSet, basename='services-names')
router.register(r'roles', DimRolesViewSet, basename='roles')
router.register(r'responsible-persons', LinkResponsiblePersonViewSet, basename='responsible-persons')
router.register(r'url-services', LinksUrlServiceViewSet, basename='url-services')
router.register(r'stack', DimStackViewSet, basename='stack')
router.register(r'service-docs', LinkDocViewSet, basename='service-docs')

# Основные URL-маршруты
urlpatterns = [
    # API
    path('api/', include(router.urls)),
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('', ServicesView.as_view(), name='services'),
    path('<int:pk>/', ServicesDetailView.as_view(), name='services-detail'),
    path('user/', ServiceUserView.as_view(), name='services-user'),
    path('link/', LinksUrlServiceListView.as_view(), name='dim-link'),
    # Graph
    path('graph/<int:pk>/', ServiceGraphView.as_view(), name='service-graph'),
    path('api/graph/<int:pk>/', ServiceGraphDataView.as_view(), name='service-graph-data'),
]
