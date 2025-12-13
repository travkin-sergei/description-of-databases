# my_dbm/serializers.py
import hashlib
from rest_framework import serializers
from .models import (
    DimStage, DimDB, LinkDB, LinkDBSchema, DimDBTableType, DimColumnName, LinkDBTable,
    LinkColumn, DimTypeLink, LinkColumnColumn, LinkColumnName, TotalData,
    hash_calculate
)


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
        fields = [
            "stand", "table_type", "group_catalog", "table_catalog",
            "table_schema", "table_name", "table_comment", "column_number",
            "column_name", "column_comment", "data_type", "is_nullable",
            "is_auto", "column_info"
        ]

    def validate(self, data):
        """Проверка обязательных полей для хэша."""
        required_for_hash = [
            'stand', 'table_catalog', 'table_schema', 'table_type',
            'table_name', 'column_name', 'data_type'
        ]

        missing_fields = [field for field in required_for_hash if not data.get(field)]

        if missing_fields:
            raise serializers.ValidationError({
                'error': f'Для расчета хеша необходимы поля: {", ".join(missing_fields)}'
            })
        return data

    def calculate_hash(self, validated_data):
        """Расчет хэша из validated_data."""
        hash_fields = [
            validated_data.get('stand', ''),
            validated_data.get('table_catalog', ''),
            validated_data.get('table_schema', ''),
            validated_data.get('table_type', ''),
            validated_data.get('table_name', ''),
            validated_data.get('column_name', ''),
            validated_data.get('data_type', ''),
        ]
        return hash_calculate(hash_fields)

    def create(self, validated_data):
        """Создает запись и возвращает только hash_address."""
        # Рассчитываем хэш
        hash_address = self.calculate_hash(validated_data)

        # Создаем или обновляем запись
        instance, created = TotalData.objects.update_or_create(
            hash_address=hash_address,
            defaults=validated_data
        )

        return instance  # Возвращаем объект, но to_representation покажет только hash

    def update(self, instance, validated_data):
        """Обновление записи."""
        # Проверяем, не меняются ли ключевые поля
        hash_fields = ['stand', 'table_catalog', 'table_schema', 'table_type',
                       'table_name', 'column_name', 'data_type']

        for field in hash_fields:
            if field in validated_data:
                current = getattr(instance, field, '')
                new = validated_data[field]
                if str(current) != str(new):
                    raise serializers.ValidationError({
                        field: f'Нельзя изменять поле {field} - оно влияет на хэш'
                    })

        # Обновляем разрешенные поля
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Возвращает ТОЛЬКО hash_address в ответе.
        """
        # ВАЖНО: возвращаем только hash_address
        return {
            'hash_address': instance.hash_address
        }
