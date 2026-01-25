# app_services/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    DimTechStackViewSet,
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
router.register(r'tech-stack', DimTechStackViewSet, basename='tech-stack')
router.register(r'service-docs', LinkDocViewSet, basename='service-docs')

# Основные URL-маршруты
urlpatterns = [
    # API-маршруты (подключаются через роутер DRF)
    path('api/', include(router.urls)),
    # Веб-маршруты (HTML-представления)
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('services/', ServicesView.as_view(), name='services'),
    path('services/<int:pk>/', ServicesDetailView.as_view(), name='services-detail'),
    path('services-user/', ServiceUserView.as_view(), name='services-user'),
    path('link/', LinksUrlServiceListView.as_view(), name='dim-link'),
]
