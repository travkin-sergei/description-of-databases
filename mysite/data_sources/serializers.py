from rest_framework import serializers
from .models import (
    DataSources,
)


class DataSourcesSerializer(serializers.ModelSerializer):
    """
    Сериализация списка источников данных
    """

    class Meta:
        model = DataSources
        fields = '__all__'
