# views/v1.py
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from app_url.models import DimUrl
from ..models import DimUpdateMethod, LinkUpdateCol
from ..serializers import DimUpdateMethodSerializer, LinkUpdateColSerializer
from ..filters import DimUpdateMethodFilter, LinkUpdateColFilter

updates_tags = ["Updates"]

read_only_schema = extend_schema_view(
    list=extend_schema(tags=updates_tags, description="Получить список методов обновления"),
    retrieve=extend_schema(tags=updates_tags, description="Получить детальную информацию о методе обновления")
)


class ReadOnlyViewSetMixin:
    http_method_names = ['get', 'head', 'options']

    def get_permissions(self):
        return [permissions.AllowAny()]


@read_only_schema
class DimUpdateMethodViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = DimUpdateMethod.objects.all()
    serializer_class = DimUpdateMethodSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DimUpdateMethodFilter
    search_fields = ['name', 'schedule', 'url__url']
    ordering_fields = ['name', 'schedule', 'created_at', 'updated_at']
    ordering = ['name', 'schedule']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('url')

        url_value = self.request.query_params.get('url')
        if url_value:
            queryset = queryset.filter(url__url=url_value)

        url_normalized = self.request.query_params.get('url_normalized')
        if url_normalized:
            queryset = queryset.filter(url__url_normalized=url_normalized)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @extend_schema(
        tags=updates_tags,
        summary="Получить методы обновления по URL",
        description="Возвращает список методов обновления для указанного URL",
        parameters=[
            OpenApiParameter(
                name='url', type=str, location=OpenApiParameter.QUERY,
                description='URL для фильтрации', required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_url(self, request):
        url_value = request.query_params.get('url')
        if not url_value:
            return Response({'error': 'Параметр url обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            url_obj = DimUrl.objects.get(url=url_value)
        except DimUrl.DoesNotExist:
            return Response({'error': f'URL не найден: {url_value}'}, status=status.HTTP_404_NOT_FOUND)

        methods = self.get_queryset().filter(url=url_obj)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data)

    @extend_schema(tags=updates_tags, summary="Получить список расписаний")
    @action(detail=False, methods=['get'])
    def schedules(self, request):
        schedules = DimUpdateMethod.objects.values_list('schedule', flat=True).distinct()
        return Response(list(schedules))

    @extend_schema(tags=updates_tags, summary="Статистика методов обновления")
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = DimUpdateMethod.objects.count()
        active = DimUpdateMethod.objects.filter(is_active=True).count()

        with_url = DimUpdateMethod.objects.filter(url__isnull=False).count()
        without_url = total - with_url

        schedule_stats = DimUpdateMethod.objects.values('schedule').annotate(
            total_count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        ).order_by('-total_count')

        url_stats = DimUpdateMethod.objects.values('url__url').annotate(
            count=Count('id')
        ).order_by('-count')

        return Response({
            'total': total, 'active': active, 'inactive': total - active,
            'with_url': with_url, 'without_url': without_url,
            'schedule_stats': list(schedule_stats), 'url_stats': list(url_stats)
        })

    @extend_schema(tags=updates_tags, summary="Информация об используемых URL")
    @action(detail=False, methods=['get'])
    def url_info(self, request):
        urls_with_methods = DimUrl.objects.filter(
            id__in=DimUpdateMethod.objects.filter(url__isnull=False).values('url_id')
        ).annotate(
            method_count=Count('dimupdatemethod'),
            active_method_count=Count('dimupdatemethod', filter=Q(dimupdatemethod__is_active=True))
        ).values('url', 'url_normalized', 'status_code', 'method_count', 'active_method_count')

        return Response(list(urls_with_methods))


@extend_schema_view(
    list=extend_schema(tags=updates_tags, description="Получить список связей обновления столбцов"),
    retrieve=extend_schema(tags=updates_tags, description="Получить детальную информацию о связи обновления столбцов")
)
class LinkUpdateColViewSet(ReadOnlyViewSetMixin, viewsets.ModelViewSet):
    queryset = LinkUpdateCol.objects.all()
    serializer_class = LinkUpdateColSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LinkUpdateColFilter
    search_fields = [
        'type__name', 'main__column__name', 'sub__column__name',
        'main__table__name', 'sub__table__name', 'type__url__url'
    ]
    ordering_fields = ['main__column__name', 'type__name', 'created_at', 'updated_at']
    ordering = ['main__column__name']

    def get_queryset(self):
        queryset = super().get_queryset()

        method_url = self.request.query_params.get('method_url')
        if method_url:
            queryset = queryset.filter(type__url__url=method_url)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        has_sub = self.request.query_params.get('has_sub')
        if has_sub is not None:
            queryset = queryset.filter(sub__isnull=has_sub.lower() != 'true')

        queryset = queryset.select_related(
            'type', 'type__url', 'main', 'main__column', 'main__table', 'main__table__database',
            'sub', 'sub__column', 'sub__table', 'sub__table__database'
        )

        return queryset

    @extend_schema(
        tags=updates_tags,
        summary="Получить связи по методу обновления",
        description="Возвращает связи обновления столбцов для указанного метода обновления",
        parameters=[
            OpenApiParameter(
                name='method_url', type=str, location=OpenApiParameter.QUERY,
                description='URL метода обновления', required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_update_method(self, request):
        method_url = request.query_params.get('method_url')
        if not method_url:
            return Response({'error': 'Параметр method_url обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        links = self.get_queryset().filter(type__url__url=method_url)
        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=updates_tags,
        summary="Получить связи по основной колонке",
        description="Возвращает связи обновления для указанной основной колонки",
        parameters=[
            OpenApiParameter(
                name='column_id', type=int, location=OpenApiParameter.QUERY,
                description='ID основной колонки', required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_main_column(self, request):
        column_id = request.query_params.get('column_id')
        if not column_id:
            return Response({'error': 'Параметр column_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        links = self.get_queryset().filter(main__column_id=column_id)
        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=updates_tags,
        summary="Получить связи по базе данных",
        description="Возвращает связи обновления для указанной базы данных",
        parameters=[
            OpenApiParameter(
                name='database_id', type=int, location=OpenApiParameter.QUERY,
                description='ID базы данных', required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_database(self, request):
        database_id = request.query_params.get('database_id')
        if not database_id:
            return Response({'error': 'Параметр database_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        links = self.get_queryset().filter(
            Q(main__table__database_id=database_id) | Q(sub__table__database_id=database_id)
        )
        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=updates_tags,
        summary="Получить связи по шаблону URL",
        description="Возвращает связи обновления, где URL метода обновления содержит указанный шаблон",
        parameters=[
            OpenApiParameter(
                name='url_pattern', type=str, location=OpenApiParameter.QUERY,
                description='Шаблон для поиска в URL', required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_url_pattern(self, request):
        url_pattern = request.query_params.get('url_pattern')
        if not url_pattern:
            return Response({'error': 'Параметр url_pattern обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        links = self.get_queryset().filter(
            Q(type__url__url__icontains=url_pattern) | Q(type__url__url_normalized__icontains=url_pattern)
        )

        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)

    @extend_schema(tags=updates_tags, summary="Статистика связей обновления")
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = LinkUpdateCol.objects.count()
        active = LinkUpdateCol.objects.filter(is_active=True).count()
        with_sub = LinkUpdateCol.objects.filter(sub__isnull=False).count()

        by_type = LinkUpdateCol.objects.values(
            'type__name', 'type__url__url', 'type__id'
        ).annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        ).order_by('-count')

        by_url = LinkUpdateCol.objects.values('type__url__url').annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        ).order_by('-count')

        return Response({
            'total': total, 'active': active, 'inactive': total - active,
            'with_sub_column': with_sub, 'without_sub_column': total - with_sub,
            'by_type': list(by_type), 'by_url': list(by_url)
        })
