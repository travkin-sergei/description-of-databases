from rest_framework import serializers
from .models import (
    Base,
    BaseGroup,
    Schema,
    Table,
    Column,
    StageColumn,
    ColumnColumn,
    Update,
    Service,
    ServiceTable
)


class BaseGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseGroup
        fields = "__all__"


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = "__all__"


class SchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schema
        fields = "__all__"


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = (
            "id", "is_active", "date_create",
            "column_name", "column_default",
            "is_nullable", "data_type", "is_auto",
            "column_com", "table", "md_type",
        )


class StageColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageColumn
        fields = (
            "is_active", "stage", "column",
        )


class ColumnColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnColumn
        fields = '__all__'


class UpdateSerializer(serializers.ModelSerializer):
    class Metahash_address:
        model = Update
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "hash_address", "service",
        )
