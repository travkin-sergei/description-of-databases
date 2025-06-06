from rest_framework import serializers
from .models import DimServices, DimServicesName


class DimServicesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimServicesName
        fields = ['id', 'name', 'created_at', 'updated_at']


class DimServicesSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = DimServices
        fields = ['id', 'alias', 'type', 'type_name', 'description', 'created_at', 'updated_at']


class DimServicesDetailSerializer(DimServicesSerializer):
    names = DimServicesNameSerializer(many=True, read_only=True, source='dimservicesname_set')

    class Meta(DimServicesSerializer.Meta):
        fields = DimServicesSerializer.Meta.fields + ['names']