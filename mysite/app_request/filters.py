import django_filters

from .models import TableGroup, ColumnGroup


class ColumnGroupFilter(django_filters.FilterSet):
    """
    Фильтры для модели ColumnGroup.
    Позволяют искать по:
    - базе данных, схеме, таблице (через связанные поля LinkTable);
    - столбцу (через LinkColumn);
    - названию группы столбцов.
    """

    # Поиск по базе данных (частичное совпадение, без учёта регистра)
    column__table__schema__base__name = django_filters.CharFilter(
        field_name='column__table__schema__base__name',
        lookup_expr='icontains',
        label='База данных',
        help_text='Поиск по названию базы данных (частичное совпадение)'
    )

    # Поиск по схеме (частичное совпадение)
    column__table__schema__schema = django_filters.CharFilter(
        field_name='column__table__schema__schema',
        lookup_expr='icontains',
        label='Схема',
        help_text='Поиск по названию схемы (частичное совпадение)'
    )

    # Поиск по названию таблицы
    column__table__name = django_filters.CharFilter(
        field_name='column__table__name',
        lookup_expr='icontains',
        label='Таблица',
        help_text='Поиск по названию таблицы (частичное совпадение)'
    )

    # Поиск по названию столбца (предполагается поле 'columns' в LinkColumn)
    column__columns = django_filters.CharFilter(
        field_name='column__columns',
        lookup_expr='icontains',
        label='Столбец',
        help_text='Поиск по названию столбца (частичное совпадение)'
    )

    # Поиск по названию группы столбцов
    group_name__name = django_filters.CharFilter(
        field_name='group_name__name',
        lookup_expr='icontains',
        label='Название группы столбцов',
        help_text='Поиск по названию группы столбцов (частичное совпадение)'
    )

    # Дополнительный фильтр: точное совпадение по ID группы столбцов
    group_name_id = django_filters.NumberFilter(
        field_name='group_name__id',
        lookup_expr='exact',
        label='ID группы столбцов',
        help_text='Поиск по точному ID группы столбцов'
    )

    # Фильтр для пустых/непустых значений (например, найти записи без указания столбца)
    column_isnull = django_filters.BooleanFilter(
        field_name='column',
        lookup_expr='isnull',
        label='Столбец указан?',
        help_text='Фильтр по наличию значения в поле "column"'
    )

    class Meta:
        model = ColumnGroup
        fields = [
            'column__table__schema__base__name',
            'column__table__schema__schema',
            'column__table__name',
            'column__columns',
            'group_name__name',
            'group_name_id',
            'column_isnull',
        ]

    @property
    def qs(self):
        """
        Добавляет:
        - сортировку по умолчанию;
        - оптимизацию запросов через select_related.
        """
        queryset = super().qs

        # Оптимизация запросов: загружаем связанные объекты сразу
        queryset = queryset.select_related(
            'column__table__schema',
            'group_name'
        )

        # Сортировка: сначала по группе, затем по столбцу
        return queryset.order_by('group_name__name', 'column__columns')


class TableGroupFilter(django_filters.FilterSet):
    """
    Фильтры для модели TableGroup.
    Позволяют искать по:
    - базе данных, схеме, таблице (через связанные поля LinkTable);
    - названию группы таблиц.
    """

    # Поиск по базе данных
    table__schema__base__name = django_filters.CharFilter(
        field_name='table__schema__base__name',
        lookup_expr='icontains',
        label='База данных',
        help_text='Поиск по названию базы данных (частичное совпадение)'
    )

    # Поиск по схеме
    table__schema__schema = django_filters.CharFilter(
        field_name='table__schema__schema',
        lookup_expr='icontains',
        label='Схема',
        help_text='Поиск по названию схемы (частичное совпадение)'
    )

    # Поиск по названию таблицы
    table__name = django_filters.CharFilter(
        field_name='table__name',
        lookup_expr='icontains',
        label='Таблица',
        help_text='Поиск по названию таблицы (частичное совпадение)'
    )

    # Поиск по названию группы таблиц
    group_name__name = django_filters.CharFilter(
        field_name='group_name__name',
        lookup_expr='icontains',
        label='Название группы таблиц',
        help_text='Поиск по названию группы таблиц (частичное совпадение)'
    )

    # Дополнительный фильтр: точное совпадение по ID группы таблиц
    group_name_id = django_filters.NumberFilter(
        field_name='group_name__id',
        lookup_expr='exact',
        label='ID группы таблиц',
        help_text='Поиск по точному ID группы таблиц'
    )

    # Фильтр по наличию таблицы
    table_isnull = django_filters.BooleanFilter(
        field_name='table',
        lookup_expr='isnull',
        label='Таблица указана?',
        help_text='Фильтр по наличию значения в поле "table"'
    )

    class Meta:
        model = TableGroup
        fields = [
            'table__schema__base__name',
            'table__schema__schema',
            'table__name',
            'group_name__name',
            'group_name_id',
            'table_isnull',
        ]

    @property
    def qs(self):
        """
        Добавляет:
        - сортировку по умолчанию;
        - оптимизацию запросов через select_related.
        """
        queryset = super().qs

        # Оптимизация: загружаем связанные объекты заранее
        queryset = queryset.select_related(
            'table__schema',
            'group_name'
        )

        # Сортировка: сначала по группе, затем по таблице
        return queryset.order_by('group_name__name', 'table__name')
