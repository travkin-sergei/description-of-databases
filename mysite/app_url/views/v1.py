# v1.py
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from ..models import DimUrl
from ..serializers import (
    DimUrlSerializer,

)
from ..permissions import DimUrlPermission


@extend_schema(tags=['app_url'])
class DimUrlViewSet(viewsets.ModelViewSet):
    """
    API для управления URL (версия v1).

    Разрешения:
    - Чтение: все аутентифицированные пользователи.
    - Создание/обновление: только админы.
    - Удаление: запрещено.
    """
    queryset = DimUrl.objects.all()
    serializer_class = DimUrlSerializer
    permission_classes = [DimUrlPermission]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return DimUrlSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['get'])
    def validate(self, request, pk=None):
        """
        Дополнительный эндпоинт для проверки валидности URL.

        Возвращает:
        - status: 'valid'/'invalid'
        - message: описание результата.
        """
        obj = get_object_or_404(self.queryset, pk=pk)
        # Здесь должна быть логика проверки URL (например, пинг, проверка статуса)
        is_valid = True  # Заменить на реальную проверку
        return Response({
            'status': 'valid' if is_valid else 'invalid',
            'message': 'URL доступен' if is_valid else 'URL недоступен'
        })
