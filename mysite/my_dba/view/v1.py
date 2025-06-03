from contextlib import suppress

from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404

from ..models import (
    BaseGroup,
    Base,
    Schema,
    Table,
    Column,
    StageColumn,
    ColumnColumn,
    Update,
    Service,
    ServiceTable
)

from ..serializers import (
    BaseGroupSerializer,
    BaseSerializer,
    SchemaSerializer,
    TableSerializer,
    ColumnSerializer,
    StageColumnSerializer,
    ColumnColumnSerializer, ServiceSerializer, UpdateSerializer,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["DBA"],
    summary="BaseGroupAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class BaseGroupAPIViewSet(ModelViewSet):
    """
    Получить список всех BaseGroup
    """
    queryset = BaseGroup.objects.all()
    serializer_class = BaseGroupSerializer


@extend_schema(
    tags=["DBA"],
    summary="BaseAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class BaseAPIViewSet(ModelViewSet):
    """
    Получить список всех Base
    """
    queryset = Base.objects.all()
    serializer_class = BaseSerializer


@extend_schema(
    tags=["DBA"],
    summary="SchemaAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class SchemaAPIViewSet(ModelViewSet):
    """
    Получить список всех Схема
    """
    queryset = Schema.objects.all()
    serializer_class = SchemaSerializer


@extend_schema(
    tags=["DBA"],
    summary="TableAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class TableAPIViewSet(ModelViewSet):
    """
    Получить список всех Table
    """
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    @extend_schema(summary='Получить 1 элемент из таблицы name_table')
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


@extend_schema(
    tags=["DBA"],
    summary="ColumnAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class ColumnAPIViewSet(ModelViewSet):
    """
    Получить список всех Column
    """
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer


@extend_schema(
    tags=["DBA"],
    summary="StageColumnAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class StageColumnAPIViewSet(ModelViewSet):
    """
    Получить список всех StageColumn
    """
    queryset = StageColumn.objects.all()
    serializer_class = StageColumnSerializer


@extend_schema(
    tags=["DBA"],
    summary="ColumnColumnAPIViewSet",
    description=(
            """
            Много
            строчный
            комментарий
            """
    ),
)
class ColumnColumnAPIViewSet(ModelViewSet):
    """
    Получить список всех ColumnColumn
    """
    queryset = ColumnColumn.objects.all()
    serializer_class = ColumnColumnSerializer


class TableDetailAPIView(APIView):
    """
    API-представление для получения данных таблицы и связанных объектов по ID таблицы.
    """

    @extend_schema(
        tags=["DBA"],
        summary="(Confluence) Получить данные таблицы по её id",
        responses={200: "Успех"},
    )
    def get(self, request, pk, *args, **kwargs):
        # Проверяем наличие объекта Table
        table = get_object_or_404(Table, pk=pk)
        # Получаем связанные данные по table_id
        columns = Column.objects.filter(table_id=table.id).order_by('date_create', 'id')
        stages = StageColumn.objects.filter(column_id__in=columns, is_active=True)
        column_columns = ColumnColumn.objects.filter(main_id__in=columns, is_active=True)
        updates = Update.objects.filter(
            pk__in=ColumnColumn.objects
            .filter(main_id__in=columns)
            .exclude(update_id__isnull=True)
            .values('update_id')
            .distinct()
        )
        services = Service.objects.filter(
            pk__in=ServiceTable.objects
            .filter(table_id=table.id, is_active=True)
            .values('service_id')
            .distinct()
        )
        # Сериализация данных
        column_data = ColumnSerializer(columns, many=True).data
        stage_data = StageColumnSerializer(stages, many=True).data
        column_column_data = ColumnColumnSerializer(column_columns, many=True).data
        update_data = UpdateSerializer(updates, many=True).data
        service_data = ServiceSerializer(services, many=True).data

        # Формируем ответ JSON
        response_data = {
            "table": {
                "table_id": table.id,
                "hash_address": table.hash_address,
                "table_name": table.table_name,
                "table_ru": table.table_ru,
                "table_com": table.table_com,
                "is_active": table.is_active,
                "is_metadata": table.is_metadata,
            },
            'service': service_data,
            'column': column_data,
            'stage': stage_data,
            'column_column': column_column_data,
            'update_column': update_data,
        }
        return Response(response_data)
