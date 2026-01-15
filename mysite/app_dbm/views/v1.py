# app_dbm/views/v1.py
from rest_framework import viewsets, permissions, filters
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, OpenApiResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (
    DimStage, DimDB, LinkDB, LinkSchema, DimTableType, DimColumnName, LinkTable, LinkColumn,
    DimTypeLink, LinkColumnColumn, LinkColumnName, TotalData
)
from ..serializers import (
    TotalDataSerializer, DimStageSerializer, DimDBSerializer, LinkDBSerializer,
    DimColumnNameSerializer, LinkColumnSerializer,
    DimTypeLinkSerializer, LinkColumnColumnSerializer, LinkColumnNameSerializer,
   # LinkSchemaSerializer, LinkTableSerializer, DimTableTypeSerializer,
)

dba_tags = ["DBM"]

# Схема только для GET методов
read_only_schema = extend_schema_view(
    list=extend_schema(tags=dba_tags),
    retrieve=extend_schema(tags=dba_tags)
)
from django.http import JsonResponse
from django.views.generic import View
from ..models import DimDB, LinkSchema, LinkTable, LinkColumn


class SchemaByDBAPI(View):
    """Получение схем по выбранной базе данных"""

    def get(self, request):
        db_id = request.GET.get('db_id')
        if not db_id:
            return JsonResponse({'error': 'No db_id provided'}, status=400)

        schemas = LinkSchema.objects.filter(base_id=db_id).values('id', 'schema')
        return JsonResponse(list(schemas), safe=False)


class TableBySchemaAPI(View):
    """Получение таблиц по выбранной схеме"""

    def get(self, request):
        schema_id = request.GET.get('schema_id')
        if not schema_id:
            return JsonResponse({'error': 'No schema_id provided'}, status=400)

        tables = LinkTable.objects.filter(schema_id=schema_id).values('id', 'name')
        return JsonResponse(list(tables), safe=False)


class ColumnByTableAPI(View):
    """Получение колонок по выбранной таблице"""

    def get(self, request):
        table_id = request.GET.get('table_id')
        if not table_id:
            return JsonResponse({'error': 'No table_id provided'}, status=400)

        columns = LinkColumn.objects.filter(table_id=table_id).values('id', 'columns')
        return JsonResponse(list(columns), safe=False)

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
# @read_only_schema
# class LinkSchemaViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
#     queryset = LinkSchema.objects.all()
#     serializer_class = LinkSchemaSerializer
#     lookup_field = 'schema'
#
#
# @read_only_schema
# class DimTableTypeViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
#     queryset = DimTableType.objects.all()
#     serializer_class = DimTableTypeSerializer
#     pagination_class = None


@read_only_schema
class DimColumnNameViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimColumnName.objects.all()
    serializer_class = DimColumnNameSerializer
    search_fields = ['name']
    ordering = ['name']


# @read_only_schema
# class LinkTableViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
#     queryset = LinkTable.objects.all()
#     serializer_class = LinkTableSerializer
#     filter_backends = [DjangoFilterBackend, SearchFilter]
#     filterset_fields = ['schema', 'type', 'is_metadata']
#     search_fields = ['name', 'description']
#
#     @extend_schema(tags=dba_tags)
#     @action(detail=True, methods=['get'])
#     def columns(self, request, pk=None):
#         table = self.get_object()
#         columns = LinkColumn.objects.filter(table=table)
#         serializer = LinkColumnSerializer(columns, many=True)
#         return Response(serializer.data)


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


from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


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
        'get',
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
        description="""
        Создает или обновляет запись в базе данных метаданных.

        **Важно:**
        - Хэш рассчитывается автоматически из ключевых полей
        - Если запись с таким хэшем уже существует, она будет обновлена
        - Возвращается только `hash_address` созданной/обновленной записи

        **Обязательные поля для расчета хэша:**
        - stand
        - table_catalog  
        - table_schema
        - table_type
        - table_name
        - column_name
        - data_type

        **Форматы данных:**
        - column_number: целое число (integer)
        - column_info: JSON объект (object) или массив (array)
        - Остальные поля: строки (string)
        """,
        request=TotalDataSerializer,
        responses={
            201: OpenApiResponse(
                response=TotalDataSerializer,
                description='Запись успешно создана или обновлена'
            ),
            400: OpenApiResponse(
                description='Ошибка валидации входных данных'
            )
        },
        examples=[
            OpenApiExample(
                'Пример создания записи о таблице',
                summary='Таблица orders',
                description='Создание записи о стобцах таблицы',
                value={
                    "stand": "production",
                    "table_type": "TABLE",
                    "group_catalog": "sales",
                    "table_catalog": "sales_db",
                    "table_schema": "public",
                    "table_name": "orders",
                    "table_comment": "Таблица заказов",
                    "column_number": 1,
                    "column_name": "order_id",
                    "column_comment": "Уникальный идентификатор заказа",
                    "data_type": "INTEGER",
                    "is_nullable": "NO",
                    "is_auto": "YES",
                    "column_info": {
                        "primary_key": True,
                        "indexed": True,
                    }
                },
                request_only=True,
                status_codes=['201']
            ),
            OpenApiExample(
                'Пример создания записи о view',
                summary='View customer_summary',
                description='Создание записи о представлении',
                value={
                    "stand": "staging",
                    "table_type": "VIEW",
                    "group_catalog": "analytics",
                    "table_catalog": "analytics_db",
                    "table_schema": "reports",
                    "table_name": "customer_summary",
                    "table_comment": "Сводка по клиентам",
                    "column_number": 3,
                    "column_name": "total_orders",
                    "column_comment": "Общее количество заказов",
                    "data_type": "BIGINT",
                    "is_nullable": "YES",
                    "is_auto": "NO",
                    "column_info": {
                        "aggregated": True,
                        "source_table": "orders",
                    }
                },
                request_only=True,
                status_codes=['201']
            ),
            OpenApiExample(
                'Пример ответа',
                summary='Успешное создание',
                description='Возвращается только hash_address записи',
                value={
                    "hash_address": "a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef"
                },
                response_only=True,
                status_codes=['201']
            ),
            OpenApiExample(
                'Пример ошибки',
                summary='Не хватает обязательных полей',
                description='Ошибка при отсутствии обязательных полей',
                value={
                    "error": "Для расчета хеша необходимы поля: stand, table_catalog"
                },
                response_only=True,
                status_codes=['400']
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        """
        Обработка создания записи.
        Если запись с таким хэшем уже существует, она будет обновлена.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @extend_schema(
        summary="Обновить запись",
        description="""Обновление записи по hash_address.

        **Ограничения:**
        - Нельзя изменять поля, участвующие в расчете хэша
        - Можно обновлять только неключевые поля
        """,
        request=TotalDataSerializer,
        responses={200: TotalDataSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление",
        description="Частичное обновление записи (только указанные поля)",
        request=TotalDataSerializer,
        responses={200: TotalDataSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить запись",
        description="Удаление записи по hash_address",
        responses={
            204: OpenApiResponse(description='Запись успешно удалена'),
            404: OpenApiResponse(description='Запись не найдена')
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
