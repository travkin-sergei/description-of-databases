from rest_framework import serializers
from .models import TableGroupName, TableGroup, ColumnGroupName, ColumnGroup



class TableGroupNameSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TableGroupName (названия групп таблиц).
    """
    class Meta:
        model = TableGroupName
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Проверяет, что название группы не пусто и уникально.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Название группы не может быть пустым.")

        # Проверка уникальности (если создаётся новый объект)
        if (
            self.instance is None and
            TableGroupName.objects.filter(name=value).exists()
        ):
            raise serializers.ValidationError(
                "Группа с таким названием уже существует."
            )
        return value.strip()



class TableGroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TableGroup (связь таблицы с группой).
    Добавляет вложенные поля:
    - table_name: название таблицы;
    - group_name_display: название группы таблиц.
    """
    table_name = serializers.CharField(
        source='table.name',
        read_only=True,
        help_text="Название таблицы (только для чтения)"
    )
    group_name_display = serializers.CharField(
        source='group_name.name',
        read_only=True,
        help_text="Название группы таблиц (только для чтения)"
    )

    class Meta:
        model = TableGroup
        fields = [
            'id',
            'table',
            'table_name',
            'group_name',
            'group_name_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Общая валидация: проверяет, что таблица и группа существуют.
        """
        table = attrs.get('table')
        group_name = attrs.get('group_name')

        if table and not table.pk:
            raise serializers.ValidationError({"table": "Таблица не найдена."})
        if group_name and not group_name.pk:
            raise serializers.ValidationError({"group_name": "Группа не найдена."})

        return attrs



class ColumnGroupNameSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ColumnGroupName (названия групп столбцов).
    """
    class Meta:
        model = ColumnGroupName
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Проверяет, что название группы столбцов не пусто и уникально.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Название группы столбцов не может быть пустым.")

        if (
            self.instance is None and
            ColumnGroupName.objects.filter(name=value).exists()
        ):
            raise serializers.ValidationError(
                "Группа столбцов с таким названием уже существует."
            )
        return value.strip()



class ColumnGroupSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ColumnGroup (связь столбца с группой).
    Добавляет вложенные поля:
    - column_name: название столбца;
    - group_name_display: название группы столбцов.
    """
    column_name = serializers.CharField(
        source='column.columns',  # Предполагаем, что поле называется 'columns'
        read_only=True,
        help_text="Название столбца (только для чтения)"
    )
    group_name_display = serializers.CharField(
        source='group_name.name',
        read_only=True,
        help_text="Название группы столбцов (только для чтения)"
    )

    class Meta:
        model = ColumnGroup
        fields = [
            'id',
            'column',
            'column_name',
            'group_name',
            'group_name_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Общая валидация: проверяет, что столбец и группа существуют.
        """
        column = attrs.get('column')
        group_name = attrs.get('group_name')

        if column and not column.pk:
            raise serializers.ValidationError({"column": "Столбец не найден."})
        if group_name and not group_name.pk:
            raise serializers.ValidationError({"group_name": "Группа столбцов не найдена."})

        return attrs
