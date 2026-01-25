# app_doc/serializers.py
from rest_framework import serializers
from .models import DimDocType, DimDoc


class DimDocTypeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели DimDocType (типы документов).
    """

    class Meta:
        model = DimDocType
        fields = [
            'id',
            'name',
            'description',
        ]
        read_only_fields = ['id']  # ID нельзя изменять

    def validate_name(self, value):
        """
        Проверяет, что название типа документа не пусто и не дублируется.
        """
        if not value:
            raise serializers.ValidationError("Название типа документа не может быть пустым.")

        # Проверка на уникальность (если создаётся новый объект)
        if (
                self.instance is None and  # Новый объект
                DimDocType.objects.filter(name=value).exists()
        ):
            raise serializers.ValidationError("Тип документа с таким названием уже существует.")
        return value


class DimDocSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели DimDoc (документы).
    Добавляет поле doc_type_name для удобного отображения.
    """
    doc_type_name = serializers.CharField(
        source='doc_type.name',
        read_only=True,
        help_text="Название типа документа (только для чтения)"
    )
    link_url = serializers.URLField(
        source='link.url',
        read_only=True,
        help_text="URL документа (только для чтения)",
        required=False
    )

    class Meta:
        model = DimDoc
        fields = [
            'id',
            'doc_type',
            'doc_type_name',
            'number',
            'date_start',
            'date_stop',
            'link',
            'link_url',
            'description',
        ]
        read_only_fields = ['id', 'doc_type_name', 'link_url']

    def validate(self, attrs):
        """
        Общая валидация документа:
        - дата окончания не может быть раньше даты начала;
        - номер документа не должен быть пустым.
        """
        date_start = attrs.get('date_start')
        date_stop = attrs.get('date_stop')

        number = attrs.get('number')

        if number and not number.strip():
            raise serializers.ValidationError({"number": "Номер документа не может быть пустым."})

        if date_start and date_stop and date_stop < date_start:
            raise serializers.ValidationError({
                "date_stop": "Дата прекращения действия не может быть раньше даты начала."
            })

        return attrs

    def validate_doc_type(self, value):
        """
        Проверяет, что тип документа существует.
        """
        if not value:
            raise serializers.ValidationError("Тип документа обязателен.")
        return value
