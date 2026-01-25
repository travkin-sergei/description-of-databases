# app_services/views/v1.py
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (
    DimServices,
    DimServicesTypes,
    DimServicesName,
    LinkResponsiblePerson,
    DimRoles,
    LinksUrlService,
    DimTechStack,
    LinkDoc,
)
from ..serializers import (
    DimServicesSerializer,
    DimServicesTypesSerializer,
    DimServicesNameSerializer,
    LinkResponsiblePersonSerializer,
    DimRolesSerializer,
    LinksUrlServiceSerializer,
    DimTechStackSerializer,
    LinkDocSerializer,
)
from ..filters import (
    DimServicesFilter,
    LinksUrlServiceFilter,
)


@extend_schema(tags=['app_services'])
class DimServicesTypesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели DimServicesTypes.
    Доступ: аутентифицированные пользователи.
    """
    queryset = DimServicesTypes.objects.all()
    serializer_class = DimServicesTypesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']  # дефолтная сортировка


@extend_schema(tags=['app_services'])
class DimServicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели DimServices.
    Оптимизирована загрузка связанных данных через prefetch_related.
    Доступ: аутентифицированные пользователи.
    """
    queryset = (
        DimServices.objects
        .prefetch_related('dimservicesname_set', 'type')
        .select_related('type')  # дополнительно загружаем type для избежания N+1
    )
    serializer_class = DimServicesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DimServicesFilter
    search_fields = ['alias', 'description']
    ordering_fields = ['alias', 'created_at']
    ordering = ['alias']


@extend_schema(tags=['app_services'])
class DimServicesNameViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели DimServicesName (синонимы сервисов).
    Оптимизирована загрузка FK-полей через select_related.
    Доступ: аутентифицированные пользователи.
    """
    queryset = DimServicesName.objects.select_related('alias', 'type')
    serializer_class = DimServicesNameSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema(tags=['app_services'])
class DimRolesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели DimRoles (роли ответственных).
    Доступ: аутентифицированные пользователи.
    """
    queryset = DimRoles.objects.all()
    serializer_class = DimRolesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema(tags=['app_services'])
class LinkResponsiblePersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели LinkResponsiblePerson (связь сервис–пользователь–роль).
    Оптимизирована загрузка связанных объектов.
    Доступ: аутентифицированные пользователи.
    """
    queryset = (
        LinkResponsiblePerson.objects
        .select_related('service', 'role', 'name__user')
    )
    serializer_class = LinkResponsiblePersonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class можно добавить при необходимости
    ordering_fields = ['service', 'role', 'created_at']
    ordering = ['service']


@extend_schema(tags=['app_services'])
class LinksUrlServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели LinksUrlService (связь URL с сервисом).
    Оптимизирована загрузка FK-полей.
    Доступ: аутентифицированные пользователи.
    """
    queryset = (
        LinksUrlService.objects
        .select_related('url', 'service', 'stage', 'stack')
    )
    serializer_class = LinksUrlServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LinksUrlServiceFilter
    search_fields = ['link_name', 'description']
    ordering_fields = ['url', 'service', 'created_at']
    ordering = ['url']


@extend_schema(tags=['app_services'])
class DimTechStackViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели DimTechStack (технологический стек).
    Доступ: аутентифицированные пользователи.
    """
    queryset = DimTechStack.objects.all()
    serializer_class = DimTechStackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema(tags=['app_services'])
class LinkDocViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели LinkDoc (связь сервиса с документом).
    Оптимизирована загрузка связанных объектов.
    Доступ: аутентифицированные пользователи.
    """
    queryset = LinkDoc.objects.select_related('services', 'doc')
    serializer_class = LinkDocSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['services', 'created_at']
    ordering = ['services']
