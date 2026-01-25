# app_request/views/v1.py
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from ..models import TableGroupName, TableGroup, ColumnGroupName, ColumnGroup
from ..serializers import (
    TableGroupNameSerializer,
    TableGroupSerializer,
    ColumnGroupNameSerializer,
    ColumnGroupSerializer,
)
from ..filters import TableGroupFilter, ColumnGroupFilter
from ..permissions import IsAdminOrEditor, IsReader


@extend_schema(tags=['app_request'])
class TableGroupNameViewSet(viewsets.ModelViewSet):
    """
    API для управления названиями групп таблиц.
    Разрешённые действия:
    - GET: все аутентифицированные пользователи (IsReader)
    - POST/PUT/PATCH/DELETE: администраторы или редакторы (IsAdminOrEditor)
    """
    queryset = TableGroupName.objects.all()
    serializer_class = TableGroupNameSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrEditor()]
        return [IsReader()]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {'error': 'Некорректные данные', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(tags=['app_request'])
class TableGroupViewSet(viewsets.ModelViewSet):
    """
    API для управления связями таблиц с группами.
    Дополнительные эндпоинты:
    - /by-group/: фильтрация по названию группы
    """
    queryset = TableGroup.objects.select_related(
        'table__schema',
        'group_name'
    ).all()
    serializer_class = TableGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TableGroupFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrEditor()]
        return [IsReader()]

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    @action(detail=False, methods=['get'], url_path='by-group')
    def by_group(self, request):
        """
        Фильтр по названию группы таблиц.
        Пример: /api/v1/table-groups/by-group/?group_name=Системные
        """
        group_name = request.query_params.get('group_name')
        if not group_name:
            return Response(
                {'error': 'Параметр group_name обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Фильтрация через Q-объекты
        queryset = self.get_queryset().filter(group_name__name=group_name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=['app_request'])
class ColumnGroupNameViewSet(viewsets.ModelViewSet):
    """
    API для управления названиями групп столбцов.
    Аналогично TableGroupNameViewSet.
    """
    queryset = ColumnGroupName.objects.all()
    serializer_class = ColumnGroupNameSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrEditor()]
        return [IsReader()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.column_groups.exists():  # Проверка на связанные ColumnGroup
            return Response(
                {'error': 'Нельзя удалить группу с привязанными столбцами'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=['app_request'])
class ColumnGroupViewSet(viewsets.ModelViewSet):
    """
    API для управления связями столбцов с группами.
    Дополнительные эндпоинты:
    - /by-column/: фильтрация по названию столбца
    """
    queryset = ColumnGroup.objects.select_related(
        'column__table__schema',
        'group_name'
    ).all()
    serializer_class = ColumnGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ColumnGroupFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrEditor()]
        return [IsReader()]

    @method_decorator(cache_page(60 * 15))
    @action(detail=False, methods=['get'], url_path='by-column')
    def by_column(self, request):
        """
        Фильтр по названию столбца.
        Пример: /api/v1/column-groups/by-column/?column=user_id
        """
        column_name = request.query_params.get('column')
        if not column_name:
            return Response(
                {'error': 'Параметр column обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Корректная фильтрация по имени столбца
        queryset = self.get_queryset().filter(column__name=column_name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
