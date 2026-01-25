import json

from rest_framework import serializers
from _common.models import hash_calculate
from .models import (
    DimStage, DimDB, LinkDB, LinkSchema, DimTableType, DimColumnName,
    LinkTable, LinkColumn, DimTypeLink, LinkColumnColumn, LinkColumnName, TotalData
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


class LinkSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkSchema
        fields = '__all__'


class DimTableTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimTableType
        fields = '__all__'


class DimColumnNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimColumnName
        fields = '__all__'


class LinkTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkTable
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
    """
    Сериализатор для модели TotalData.
    Особенности:
    - Валидация ключевых полей для хэша.
    - Обработка JSON в поле column_info.
    - Возврат только hash_address в ответе.
    """

    column_number = serializers.IntegerField(required=False, allow_null=True)
    column_info = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = TotalData
        fields = [
            'stand', 'table_type', 'group_catalog', 'table_catalog',
            'table_schema', 'table_name', 'table_comment', 'column_number',
            'column_name', 'column_comment', 'data_type', 'is_nullable',
            'is_auto', 'column_info'
        ]
        extra_kwargs = {
            'stand': {'allow_blank': True, 'allow_null': True},
            'table_type': {'allow_blank': True, 'allow_null': True},
            'group_catalog': {'allow_blank': True, 'allow_null': True},
            'table_catalog': {'allow_blank': True, 'allow_null': True},
            'table_schema': {'allow_blank': True, 'allow_null': True},
            'table_name': {'allow_blank': True, 'allow_null': True},
            'table_comment': {'allow_blank': True, 'allow_null': True},
            'column_name': {'allow_blank': True, 'allow_null': True},
            'column_comment': {'allow_blank': True, 'allow_null': True},
            'data_type': {'allow_blank': True, 'allow_null': True},
            'is_nullable': {'allow_blank': True, 'allow_null': True},
            'is_auto': {'allow_blank': True, 'allow_null': True},
        }

    def validate(self, data):
        """
        Проверяет наличие обязательных полей для расчёта хэша.
        """
        required_fields = [
            'stand', 'table_catalog', 'table_schema',
            'table_type', 'table_name', 'column_name', 'data_type'
        ]

        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise serializers.ValidationError({
                'error': f'Обязательны поля для хэша: {", ".join(missing)}'
            })
        return data

    def validate_column_number(self, value):
        """Проверяет, что column_number ≥ 0."""
        if value is not None and value < 0:
            raise serializers.ValidationError('column_number не может быть отрицательным')
        return value

    def validate_column_info(self, value):
        """
        Преобразует строку в JSON, если необходимо.
        Принимает: dict, list, str (с валидным JSON), None.
        """
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError('column_info должен быть валидным JSON')

        if isinstance(value, (dict, list)):
            return value

        raise serializers.ValidationError(
            'column_info должен быть JSON-объектом, массивом или строкой с JSON'
        )

    def calculate_hash(self, validated_data):
        """Рассчитывает хэш на основе ключевых полей."""
        fields = [
            validated_data.get('stand', ''),
            validated_data.get('table_catalog', ''),
            validated_data.get('table_schema', ''),
            validated_data.get('table_type', ''),
            validated_data.get('table_name', ''),
            validated_data.get('column_name', ''),
            validated_data.get('data_type', '')
        ]
        return hash_calculate(fields)

    def create(self, validated_data):
        """Создаёт запись с уникальным hash_address."""
        hash_address = self.calculate_hash(validated_data)
        instance, _ = TotalData.objects.update_or_create(
            hash_address=hash_address,
            defaults=validated_data
        )
        return instance

    def update(self, instance, validated_data):
        """
        Обновляет запись, запрещая изменение ключевых полей (влияющих на хэш).
        """
        key_fields = [
            'stand', 'table_catalog', 'table_schema',
            'table_type', 'table_name', 'column_name', 'data_type'
        ]

        for field in key_fields:
            if field in validated_data:
                current_val = getattr(instance, field, '')
                new_val = validated_data[field]
                if str(current_val) != str(new_val):
                    raise serializers.ValidationError({
                        field: f'Поле {field} нельзя изменить — оно влияет на hash_address'
                    })

        # Обновляем остальные поля
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Возвращает только hash_address в ответе API.
        """
        return {'hash_address': instance.hash_address}
