from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Asset
#from ..serializers import AssetSerializer
from ..filters import AssetFilter

#
# class DataAssetAPIViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint для источников данных (Asset).
#     Поддерживает поиск, фильтрацию и CRUD.
#     """
#     queryset = Asset.objects.select_related(
#         'type', 'domain', 'details'
#     ).prefetch_related('columns').all()
#
#     serializer_class = AssetSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_class = AssetFilter
#     search_fields = ['version', 'description', 'res_url', 'type__name', 'domain__name', 'details__name']
#     ordering_fields = ['version', 'created_at', 'updated_at']
#     ordering = ['-created_at']
