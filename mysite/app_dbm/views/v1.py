# app_dbm/views/v1.py

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_list_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from ..models import (
    DimStage, DimDB, LinkDB, LinkSchema,
    LinkTable, LinkColumn, DimColumnName,
    DimTypeLink, LinkColumnColumn, LinkColumnName, TotalData
)
from ..serializers import (
    DimStageSerializer, DimDBSerializer, LinkDBSerializer,
    LinkSchemaSerializer, LinkTableSerializer, LinkColumnSerializer,
    DimColumnNameSerializer, DimTypeLinkSerializer,
    LinkColumnColumnSerializer, LinkColumnNameSerializer,
    TotalDataSerializer
)
from ..permissions import TotalDataPermissions, IsDBA, IsAnalyst

# === Базовый класс для справочников ===

class ReadOnlyModelViewSet(ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]


# === ViewSet'ы ===

@extend_schema(tags=['app_dbm'])
class DimStageViewSet(ReadOnlyModelViewSet):
    queryset = DimStage.objects.all()
    serializer_class = DimStageSerializer
    permission_classes = [IsAuthenticated, IsDBA]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']

    @extend_schema(
        tags=['Слои данных'],
        summary="Активные стенды",
        description="Возвращает только активные записи (is_active=True)",
        responses={200: DimStageSerializer(many=True)}
    )
    def active(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=['app_dbm'])
class DimDBViewSet(ReadOnlyModelViewSet):
    queryset = DimDB.objects.all()
    serializer_class = DimDBSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['version', 'name']
    search_fields = ['name', 'description']


@extend_schema(tags=['app_dbm'])
class LinkDBViewSet(ReadOnlyModelViewSet):
    queryset = LinkDB.objects.select_related('base', 'stage').all()
    serializer_class = LinkDBSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['base', 'stage', 'name', 'host']

    def get_queryset(self):
        queryset = super().get_queryset()
        stage_name = self.request.query_params.get('stage')
        if stage_name:
            queryset = queryset.filter(stage__name=stage_name)
        return queryset


@extend_schema(tags=['app_dbm'])
class LinkSchemaViewSet(ReadOnlyModelViewSet):
    queryset = LinkSchema.objects.select_related('base').all()
    serializer_class = LinkSchemaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['base']
    search_fields = ['schema']


@extend_schema(tags=['app_dbm'])
class LinkTableViewSet(ReadOnlyModelViewSet):
    queryset = LinkTable.objects.select_related('schema__base', 'type').all()
    serializer_class = LinkTableSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['schema', 'type', 'is_metadata']
    search_fields = ['name']


@extend_schema(tags=['app_dbm'])
class DimColumnNameViewSet(ReadOnlyModelViewSet):
    queryset = DimColumnName.objects.all()
    serializer_class = DimColumnNameSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


@extend_schema(tags=['app_dbm'])
class LinkColumnViewSet(ReadOnlyModelViewSet):
    queryset = LinkColumn.objects.select_related('table__schema__base').all()
    serializer_class = LinkColumnSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table', 'is_key', 'is_null']


@extend_schema(tags=['app_dbm'])
class DimTypeLinkViewSet(ReadOnlyModelViewSet):
    queryset = DimTypeLink.objects.all()
    serializer_class = DimTypeLinkSerializer


@extend_schema(tags=['app_dbm'])
class LinkColumnColumnViewSet(ReadOnlyModelViewSet):
    queryset = LinkColumnColumn.objects.select_related('type', 'main', 'sub').all()
    serializer_class = LinkColumnColumnSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'main', 'sub']


@extend_schema(tags=['app_dbm'])
class LinkColumnNameViewSet(ReadOnlyModelViewSet):
    queryset = LinkColumnName.objects.select_related('column', 'name').all()
    serializer_class = LinkColumnNameSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['column', 'name']


# === Основной API: TotalData ===

@extend_schema(tags=['app_dbm'])
class TotalDataViewSet(ModelViewSet):
    """
    Управление метаданными таблиц и колонок.
    Поддерживает полный CRUD с автоматическим расчётом хэша.
    """
    queryset = TotalData.objects.all()
    serializer_class = TotalDataSerializer
    permission_classes = [TotalDataPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'table_catalog': ['exact', 'icontains'],
        'table_name': ['exact', 'icontains'],
        'data_type': ['exact'],
        'stand': ['exact']
    }
    search_fields = ['table_catalog', 'table_name', 'column_name', 'column_comment']
    ordering_fields = ['table_catalog', 'table_name', 'column_name']
    ordering = ['table_catalog', 'table_name']

    @extend_schema(
        summary="Список записей",
        parameters=[
            OpenApiParameter('table_catalog', str, description='Фильтр по имени БД'),
            OpenApiParameter('table_name', str, description='Фильтр по имени таблицы'),
            OpenApiParameter('search', str, description='Поиск по полям'),
            OpenApiParameter('ordering', str, description='Сортировка'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Детали записи")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создать или обновить запись",
        description=(
                "Создаёт новую запись или обновляет существующую по хэшу.\n"
                "Хэш генерируется автоматически из ключевых полей."
        ),
        request=TotalDataSerializer,
        responses={
            201: OpenApiResponse(response=TotalDataSerializer),
            200: OpenApiResponse(description="Запись обновлена"),
            400: OpenApiResponse(description="Ошибка валидации")
        },
        examples=[
            OpenApiExample(
                'Пример создания',
                value={
                    "stand": "production",
                    "table_type": "TABLE",
                    "group_catalog": "sales",
                    "table_catalog": "sales_db",
                    "table_schema": "public",
                    "table_name": "orders",
                    "column_name": "order_id",
                    "data_type": "INTEGER",
                    "is_nullable": "NO"
                },
                request_only=True
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(summary="Полное обновление записи")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(summary="Частичное обновление записи")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить запись",
        responses={204: OpenApiResponse(description="Успешно удалено")}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
