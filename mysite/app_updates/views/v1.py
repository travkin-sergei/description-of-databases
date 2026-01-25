from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes
from app_url.models import DimUrl
from ..models import DimUpdateMethod, LinkUpdateCol
from ..serializers import DimUpdateMethodSerializer, LinkUpdateColSerializer
from ..filters import DimUpdateMethodFilter, LinkUpdateColFilter


@extend_schema_view(
    list=extend_schema(
        tags=['app_updates'],  # ИСПРАВЛЕНО: tags должен быть списком
        description="Получить список методов обновления",
        responses={200: DimUpdateMethodSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['app_updates'],  # ИСПРАВЛЕНО
        description="Получить детальную информацию о методе обновления",
        responses={200: DimUpdateMethodSerializer}
    )
)
class DimUpdateMethodViewSet(viewsets.ReadOnlyModelViewSet):  # ЗАМЕНА: используем ReadOnlyModelViewSet вместо кастомного mixin
    """
    ViewSet для модели DimUpdateMethod (методы обновления).

    Поддерживает:
    - Фильтрацию, поиск и сортировку.
    - Дополнительные действия (actions) для специфичных запросов.
    """
    queryset = DimUpdateMethod.objects.select_related('url').all()  # select_related вынесен сюда для оптимизации
    serializer_class = DimUpdateMethodSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DimUpdateMethodFilter
    search_fields = ['name', 'schedule', 'url__url']
    ordering_fields = ['name', 'schedule', 'created_at', 'updated_at']
    ordering = ['name', 'schedule']

    @extend_schema(
        tags=['app_updates'],
        summary="Получить методы обновления по URL",
        description="Возвращает список методов обновления для указанного URL",
        parameters=[
            OpenApiParameter(
                name='url',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='URL для фильтрации',
                required=True
            )
        ],
        responses={200: DimUpdateMethodSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_url(self, request):
        url_value = request.query_params.get('url')
        if not url_value:
            return Response(
                {'error': 'Параметр url обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Оптимизированный запрос с select_related
            url_obj = DimUrl.objects.select_related('dimupdatemethod_set').get(url=url_value)
        except DimUrl.DoesNotExist:
            return Response(
                {'error': f'URL не найден: {url_value}'},
                status=status.HTTP_404_NOT_FOUND
            )

        methods = self.get_queryset().filter(url=url_obj)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['app_updates'],
        summary="Получить список расписаний",
        responses={200: {'type': 'array', 'items': {'type': 'string'}}}
    )
    @action(detail=False, methods=['get'])
    def schedules(self, request):
        schedules = DimUpdateMethod.objects.values_list('schedule', flat=True).distinct().order_by('schedule')
        return Response(list(schedules))

    @extend_schema(
        tags=['app_updates'],
        summary="Статистика методов обновления",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total': {'type': 'integer'},
                    'active': {'type': 'integer'},
                    'url_stats': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'url': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = DimUpdateMethod.objects.count()
        active = DimUpdateMethod.objects.filter(is_active=True).count()

        # Оптимизированная статистика по URL
        url_stats = DimUrl.objects.filter(
            dimupdatemethod__isnull=False
        ).annotate(
            count=Count('dimupdatemethod')
        ).values('url', 'count').order_by('-count')[:10]  # Ограничение для производительности

        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'url_stats': list(url_stats)
        })

    @extend_schema(
        tags=['app_updates'],
        summary="Информация об используемых URL",
        responses={
            200: {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'url': {'type': 'string'},
                        'method_count': {'type': 'integer'}
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def url_info(self, request):
        # Исправлено: используем правильное имя обратной связи
        urls_with_methods = DimUrl.objects.filter(
            dimupdatemethod__isnull=False
        ).annotate(
            method_count=Count('dimupdatemethod')
        ).values(
            'url', 'method_count'
        ).order_by('-method_count')[:20]  # Ограничение для производительности

        return Response(list(urls_with_methods))


@extend_schema_view(
    list=extend_schema(
        tags=['app_updates'],  # ИСПРАВЛЕНО
        description="Получить список связей обновления столбцов",
        responses={200: LinkUpdateColSerializer(many=True)}
    ),
    retrieve=extend_schema(
        tags=['app_updates'],  # ИСПРАВЛЕНО
        description="Получить детальную информацию о связи обновления столбцов",
        responses={200: LinkUpdateColSerializer}
    )
)
class LinkUpdateColViewSet(viewsets.ReadOnlyModelViewSet):  # ЗАМЕНА: используем ReadOnlyModelViewSet
    """
    ViewSet для модели LinkUpdateCol (связи методов обновления с колонками).
    """
    queryset = LinkUpdateCol.objects.select_related(
        'type', 'type__url', 'main__column', 'main__table__database',
        'sub__column', 'sub__table__database'
    ).all()
    serializer_class = LinkUpdateColSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LinkUpdateColFilter
    search_fields = [
        'type__name', 'main__column__name', 'sub__column__name',
        'main__table__name', 'sub__table__name', 'type__url__url'
    ]
    ordering_fields = ['main__column__name', 'type__name', 'created_at']
    ordering = ['main__column__name']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Исправлена логика фильтрации по has_sub
        has_sub = self.request.query_params.get('has_sub')
        if has_sub is not None:
            queryset = queryset.filter(sub__isnull=(has_sub.lower() != 'true'))

        return queryset

    @extend_schema(
        tags=['app_updates'],
        summary="Получить связи по шаблону URL",
        parameters=[
            OpenApiParameter(
                name='url_pattern',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Шаблон для поиска в URL (регистронезависимый)',
                required=True
            )
        ],
        responses={200: LinkUpdateColSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_url_pattern(self, request):
        url_pattern = request.query_params.get('url_pattern', '').strip()
        if not url_pattern:
            return Response(
                {'error': 'Параметр url_pattern обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Исправлено: используем icontains для регистронезависимого поиска
        links = self.get_queryset().filter(
            Q(type__url__url__icontains=url_pattern) |
            Q(type__url__url_normalized__icontains=url_pattern)
        ).distinct()

        page = self.paginate_queryset(links)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['app_updates'],
        summary="Статистика связей обновления (упрощённая)",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total': {'type': 'integer'},
                    'by_type': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type_name': {'type': 'string'},
                                'count': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = LinkUpdateCol.objects.count()

        # Упрощённая статистика с ограничением количества результатов
        by_type = LinkUpdateCol.objects.values(
            type_name=F('type__name')
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return Response({
            'total': total,
            'by_type': list(by_type)
        })