# app_dict/serializers.py
from rest_framework import serializers
from .models import DimCategory, DimDictionary


class DictionaryFilterSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=False,
        help_text="Частичное совпадение названия"
    )
    category__name = serializers.CharField(
        required=False,
        help_text="Частичное совпадение названия категории"
    )
    ordering = serializers.CharField(
        required=False,
        help_text="Поле для сортировки (например, 'name', '-category__name')"
    )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = DimCategory
        fields = ['id', 'name']  # Можно заменить на '__all__'


class DictionarySerializer(serializers.ModelSerializer):
    """Сериализатор для словаря терминов."""
    # Вложенное представление категории (только для чтения)
    category = CategorySerializer(read_only=True)
    # Поле для записи/обновления (принимает ID категории)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=DimCategory.objects.all(),
        write_only=True,
        source='category',
        label='ID категории'
    )

    class Meta:
        model = DimDictionary
        fields = [
            'id', 'name', 'category', 'category_id',
            'description'
        ]
        # Или: fields = '__all__' (если нет скрытых полей)

    def validate_name(self, value):
        """Проверка уникальности имени в рамках категории."""
        category = self.initial_data.get('category_id')
        if category and DimDictionary.objects.filter(
                name=value, category=category
        ).exists():
            raise serializers.ValidationError(
                "Термин с таким именем уже существует в данной категории."
            )
        return value

    def to_representation(self, instance):
        """Добавляем category_id в ответ для удобства фронтенда."""
        representation = super().to_representation(instance)
        representation['category_id'] = instance.category.id
        return representation
