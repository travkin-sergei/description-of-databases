# my_dbm/views/v1.py
from rest_framework import viewsets, permissions, filters
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (
    DimStage, DimDB, LinkDB, LinkDBSchema, DimDBTableType, DimColumnName, LinkDBTable, LinkColumn,
    DimTypeLink, LinkColumnColumn, LinkColumnName, TotalData
)
from ..serializers import (
    TotalDataSerializer, DimStageSerializer, DimDBSerializer, LinkDBSerializer, LinkDBSchemaSerializer,
    DimDBTableTypeSerializer, DimColumnNameSerializer, LinkDBTableSerializer, LinkColumnSerializer,
    DimTypeLinkSerializer, LinkColumnColumnSerializer, LinkColumnNameSerializer
)

dba_tags = ["DBM"]

# Схема только для GET методов
read_only_schema = extend_schema_view(
    list=extend_schema(tags=dba_tags),
    retrieve=extend_schema(tags=dba_tags)
)


# Базовый класс с ограничением методов
class ReadOnlyViewSetMixin:
    http_method_names = ['get', 'head', 'options']  # Разрешаем только GET запросы

    def get_permissions(self):
        # По умолчанию требуем аутентификации для всех запросов
        return [permissions.IsAuthenticated()]


@read_only_schema
class DimStageViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimStage.objects.all()
    serializer_class = DimStageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']

    @extend_schema(tags=dba_tags)
    @action(detail=False, methods=['get'])
    def active(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@read_only_schema
class DimDBViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimDB.objects.all()
    serializer_class = DimDBSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['version', 'name']
    search_fields = ['name', 'description']

    def get_permissions(self):
        # Можно переопределить permissions для конкретного ViewSet
        return [permissions.IsAuthenticated()]


@read_only_schema
class LinkDBViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkDB.objects.all()
    serializer_class = LinkDBSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['data_base', 'stage', 'name', 'host']

    def get_queryset(self):
        queryset = super().get_queryset()
        stage = self.request.query_params.get('stage', None)
        if stage:
            queryset = queryset.filter(stage__name=stage)
        return queryset


# Остальные ViewSet'ы с аналогичной структурой
@read_only_schema
class LinkDBSchemaViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkDBSchema.objects.all()
    serializer_class = LinkDBSchemaSerializer
    lookup_field = 'schema'


@read_only_schema
class DimDBTableTypeViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimDBTableType.objects.all()
    serializer_class = DimDBTableTypeSerializer
    pagination_class = None


@read_only_schema
class DimColumnNameViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimColumnName.objects.all()
    serializer_class = DimColumnNameSerializer
    search_fields = ['name']
    ordering = ['name']


@read_only_schema
class LinkDBTableViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkDBTable.objects.all()
    serializer_class = LinkDBTableSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['schema', 'type', 'is_metadata']
    search_fields = ['name', 'description']

    @extend_schema(tags=dba_tags)
    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None):
        table = self.get_object()
        columns = LinkColumn.objects.filter(table=table)
        serializer = LinkColumnSerializer(columns, many=True)
        return Response(serializer.data)


@read_only_schema
class LinkColumnViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkColumn.objects.all()
    serializer_class = LinkColumnSerializer
    filterset_fields = ['table', 'is_key', 'is_null']


@read_only_schema
class DimTypeLinkViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimTypeLink.objects.all()
    serializer_class = DimTypeLinkSerializer


@read_only_schema
class LinkColumnColumnViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkColumnColumn.objects.all()
    serializer_class = LinkColumnColumnSerializer
    filterset_fields = ['type', 'main', 'sub']


@read_only_schema
class LinkColumnNameViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkColumnName.objects.all()
    serializer_class = LinkColumnNameSerializer


@extend_schema(
    tags=['DBM'],
    description='API v1 для работы с описанием баз данных'
)
class TotalDataViewSet(viewsets.ModelViewSet):
    """
    API v1 для TotalData.
    Разрешает только GET (чтение) и POST (создание).
    """
    queryset = TotalData.objects.all()
    serializer_class = TotalDataSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Фильтрация, поиск, сортировка
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

    # Только GET и POST методы
    http_method_names = [
        #'get',
        'post',
        # 'head', 'options'
    ]

    @extend_schema(
        summary="Список всех записей",
        description="Возвращает список с пагинацией, фильтрацией и поиском",
        parameters=[
            OpenApiParameter('table_catalog', str, description='Фильтр по имени БД'),
            OpenApiParameter('table_name', str, description='Фильтр по имени таблицы'),
            OpenApiParameter('search', str, description='Поиск по нескольким полям'),
            OpenApiParameter('ordering', str, description='Сортировка (table_catalog, table_name, column_name)'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Детали записи")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создать запись",
        request=TotalDataSerializer,
        responses={201: TotalDataSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
