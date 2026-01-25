# app_dict/views/v1.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
)
from django_filters import rest_framework as django_filters

from ..models import DimCategory, DimDictionary
from ..serializers import CategorySerializer, DictionarySerializer
from ..filters import DictionaryFilter
from ..permissions import IsDBA, IsAnalyst


@extend_schema(tags=['app_dict'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Управление категориями справочных данных.
    Доступно для DBA и аналитиков.
    """
    queryset = DimCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsDBA | IsAnalyst]
    filter_backends = [filters.SearchFilter, django_filters.DjangoFilterBackend]
    search_fields = ['name']


@extend_schema(tags=['app_dict'])
class DictionaryViewSet(viewsets.ModelViewSet):
    """
    Управление словарём терминов и их синонимами.
    Доступно для всех аутентифицированных пользователей.
    """
    queryset = DimDictionary.objects.select_related('category').all()
    serializer_class = DictionarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = DictionaryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category__name']
    ordering = ['name']
    pagination_class = None  # отключена пагинация, как в требованиях