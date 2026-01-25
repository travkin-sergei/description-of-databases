# app_doc/views/v1.py

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import DimDocType, DimDoc
from ..serializers import DimDocTypeSerializer, DimDocSerializer


@extend_schema(tags=['app_doc'])
class DimDocTypeViewSet(viewsets.ModelViewSet):
    """
    Управление типами документов.
    """
    queryset = DimDocType.objects.all()
    serializer_class = DimDocTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema(tags=['app_doc'])
class DimDocViewSet(viewsets.ModelViewSet):
    """
    Управление документами.
    """
    queryset = DimDoc.objects.select_related('doc_type', 'link').all()
    serializer_class = DimDocSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['number', 'description']
    filterset_fields = ['doc_type', 'date_start', 'date_stop']
    ordering_fields = ['date_start', 'date_stop', 'number']
    ordering = ['-date_start']