from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404

from ..models import (
    DataSources,
)

from ..serializers import (
 DataSourcesSerializer,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Data Sources"],
    summary="BaseGroupAPIViewSet",
    description=(
    """
    Много
    строчный
    комментарий
    """
    ),
)
class DataSourcesAPIViewSet(ModelViewSet):
    """
    Получить список всех BaseGroup
    """
    queryset = DataSources.objects.all()
    serializer_class = DataSourcesSerializer

    @extend_schema(
        description="Описание вашего эндпоинта."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)