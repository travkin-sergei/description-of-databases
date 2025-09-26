# my_dbm/serializers.py
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from .models import *


class DimStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimStage
        fields = '__all__'


class DimDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimDB
        fields = '__all__'


class LinkDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkDB
        fields = '__all__'


class LinkDBSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkDBSchema
        fields = '__all__'


class DimDBTableTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimDBTableType
        fields = '__all__'


class DimColumnNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimColumnName
        fields = '__all__'


class LinkDBTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkDBTable
        fields = '__all__'


class LinkColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkColumn
        fields = '__all__'


class DimTypeLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimTypeLink
        fields = '__all__'


class LinkColumnColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkColumnColumn
        fields = '__all__'


class LinkColumnNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkColumnName
        fields = '__all__'


class TotalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalData
        fields = '__all__'
