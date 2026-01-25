# app_auth/views/v1.py
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from ..serializers import RegistrationRequestSerializer, DimProfileSerializer
from ..models import DimProfile


@extend_schema(
    tags=['app_auth'],
    summary="Создать заявку на регистрацию",
    description="Публичный эндпоинт для подачи заявки на регистрацию. "
                "Администратор вручную создаёт аккаунт после одобрения.",
    request=RegistrationRequestSerializer,
    responses={
        201: RegistrationRequestSerializer,
        400: {"description": "Ошибки валидации"},
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                "email": "user@example.com",
                "description": "Необходим доступ к документации сервисов"
            },
            request_only=True,
        )
    ]
)
class RegisterRequestView(APIView):
    """
    Создать заявку на регистрацию (публичный API).
    """
    permission_classes = [AllowAny]
    serializer_class = RegistrationRequestSerializer  # ← явно указано для drf-spectacular

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['app_auth'],
    summary="Получить или частично обновить профиль",
    description="Требуется аутентификация по токену. "
                "Работает с моделью DimProfile, связанной с пользователем.",
    request=DimProfileSerializer,
    responses={
        200: DimProfileSerializer,
        400: {"description": "Ошибки валидации"},
        404: {"description": "Профиль не найден"},
    }
)
class ProfileDetailView(APIView):
    """
    Получить или обновить профиль текущего пользователя.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DimProfileSerializer  # ← явно указано для drf-spectacular

    def get_object(self):
        return get_object_or_404(DimProfile, user=self.request.user)

    def get(self, request):
        profile = self.get_object()
        serializer = self.serializer_class(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = self.get_object()
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
