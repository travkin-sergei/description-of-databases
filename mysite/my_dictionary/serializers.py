from rest_framework import serializers
from .models import DimCategory, DimDictionary


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DimCategory
        fields = ['id', 'name']


class DictionarySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = DimDictionary
        fields = ['id', 'name', 'category', 'description', 'is_active']