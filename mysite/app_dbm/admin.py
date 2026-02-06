# app_dbm/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TotalData, DimStage, DimDB, LinkDB, LinkSchema, DimTableType,
    DimColumnName, DimTableNameType, LinkTable, LinkTableName,
    LinkColumn, DimTypeLink, LinkColumnColumn, LinkColumnName
)


# ================== БАЗОВЫЕ КЛАССЫ ==================
class BaseAdmin(admin.ModelAdmin):
    """Базовый класс с общими настройками"""
    list_per_page = 100
    show_full_result_count = False
    ordering = ['-created_at']  # Сортировка по умолчанию


# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================
def format_full_path(obj, color='#1890ff'):
    """Форматирование полного пути с цветом"""
    try:
        base = obj.table.schema.base.name if obj.table.schema.base else '???'
        schema = obj.table.schema.schema if obj.table.schema else '???'
        table = obj.table.name if obj.table else '???'
        column = obj.columns

        return format_html(
            '<div style="font-family: monospace; font-size: 11px; line-height: 1.3;">'
            '<span style="color: #666;">{}.{}.{}.</span>'
            '<span style="color: {}; font-weight: bold;">{}</span>'
            '</div>',
            base, schema, table, color, column
        )
    except AttributeError:
        return str(obj)[:50]


# ================== ИНЛАЙНЫ ==================
# ================== ИНЛАЙНЫ ==================
class LinkColumnInline(admin.TabularInline):
    """Инлайн для столбцов таблицы"""
    model = LinkColumn
    extra = 0
    fields = ('columns', 'type', 'is_key', 'is_null', 'description')
    show_change_link = True
    autocomplete_fields = ['table']

    def get_queryset(self, request):
        """Оптимизация запросов для инлайна"""
        return super().get_queryset(request).select_related(
            'table__schema__base'
        )


class LinkTableNameInline(admin.TabularInline):
    """Инлайн для альтернативных названий таблицы"""
    model = LinkTableName
    extra = 0
    fields = ('name', 'type', 'is_publish')  # Убрал 'description' — такого поля нет в модели
    show_change_link = True
    autocomplete_fields = ['type']
    verbose_name = 'Альтернативное название'
    verbose_name_plural = 'Альтернативные названия'

    def get_queryset(self, request):
        """Оптимизация запросов для инлайна"""
        return super().get_queryset(request).select_related(
            'type'
        )


# ================== АДМИНКИ МОДЕЛЕЙ ==================

# --- Основные модели ---
@admin.register(DimStage)
class DimStageAdmin(BaseAdmin):
    """Админка для стендов"""
    list_display = ('name', 'description')
    search_fields = ('name__istartswith',)
    ordering = ['name']


@admin.register(DimTypeLink)
class DimTypeLinkAdmin(BaseAdmin):
    """Админка для типов связей"""
    list_display = ('name',)
    search_fields = ('name__istartswith',)
    ordering = ['name']


@admin.register(DimDB)
class DimDBAdmin(BaseAdmin):
    """Админка для баз данных"""
    list_display = ('name', 'version', 'description')
    search_fields = ('name__istartswith', 'version__istartswith')
    ordering = ['name']


@admin.register(DimTableType)
class DimTableTypeAdmin(BaseAdmin):
    """Админка для типов таблиц"""
    list_display = ('name', 'description')
    search_fields = ('name__istartswith',)
    ordering = ['name']


@admin.register(DimColumnName)
class DimColumnNameAdmin(BaseAdmin):
    """Админка для названий столбцов"""
    list_display = ('name',)
    search_fields = ('name__istartswith',)
    list_per_page = 200
    ordering = ['name']


@admin.register(DimTableNameType)
class DimTableNameTypeAdmin(BaseAdmin):
    """Админка для типов названий таблиц"""
    list_display = ('name',)
    search_fields = ('name__istartswith',)
    ordering = ['name']


# --- Связанные модели с внешними ключами ---
@admin.register(LinkDB)
class LinkDBAdmin(BaseAdmin):
    """Админка для связей баз данных"""
    list_display = ('name', 'alias', 'host', 'port', 'stage', 'base')
    list_filter = ('stage', 'base')
    search_fields = ('name__istartswith', 'alias__istartswith')
    autocomplete_fields = ['base', 'stage']
    list_select_related = ('stage', 'base')
    ordering = ['alias']


@admin.register(LinkSchema)
class LinkSchemaAdmin(BaseAdmin):
    """Админка для схем"""
    list_display = ('schema', 'base', 'description')
    list_filter = ('base',)
    search_fields = ('schema__istartswith',)
    autocomplete_fields = ['base']
    list_select_related = ('base',)
    ordering = ['schema']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('base')


@admin.register(LinkTable)
class LinkTableAdmin(BaseAdmin):
    """Админка для таблиц"""
    list_display = ('name', 'schema_display', 'type', 'is_metadata')
    search_fields = ('name__istartswith', 'schema__schema__istartswith')
    autocomplete_fields = ['schema', 'type']
    list_select_related = ('schema__base', 'type')
    inlines = [LinkTableNameInline, LinkColumnInline]  # Добавлен LinkTableNameInline
    ordering = ['name']

    def schema_display(self, obj):
        return f"{obj.schema.base.name}.{obj.schema.schema}"

    schema_display.short_description = 'Схема'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'schema__base', 'type'
        )

@admin.register(LinkTableName)
class LinkTableNameAdmin(BaseAdmin):
    """Админка для альтернативных названий таблиц"""
    list_display = ('name', 'table', 'type', 'is_publish')
    list_filter = ('type', 'is_publish')
    search_fields = ('name__istartswith', 'table__name__istartswith')
    autocomplete_fields = ['table', 'type']
    list_select_related = ('table__schema__base', 'type')
    ordering = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'table__schema__base', 'type'
        )


@admin.register(LinkColumn)
class LinkColumnAdmin(BaseAdmin):
    """Админка для столбцов"""

    search_fields = (
        'columns',
        'table__name',
        'table__schema__schema',
        'table__schema__base__name',
        'type'
    )

    list_display = (
        'id',
        'full_path_display',
        'type',
        'is_key',
        'is_null',
        'created_at'
    )

    list_filter = ('is_key', 'is_null', 'table__schema__base')
    autocomplete_fields = ['table']
    list_select_related = ('table__schema__base',)
    ordering = ['-created_at']

    fields = (
        'table', 'columns', 'type', 'is_null', 'is_key',
        'unique_together', 'default', 'description', 'stage'
    )

    def full_path_display(self, obj):
        """Отображаем полный путь столбца"""
        return format_full_path(obj, color='#1890ff')

    full_path_display.short_description = 'Полный путь столбца'
    full_path_display.admin_order_field = 'table__name'

    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'table__schema__base'
        )


@admin.register(LinkColumnName)
class LinkColumnNameAdmin(BaseAdmin):
    """Админка для названий столбцов"""
    list_display = ('name', 'column_display')
    search_fields = ('name__name__istartswith', 'column__columns__istartswith')
    autocomplete_fields = ['column', 'name']
    list_select_related = ('column__table__schema__base', 'name')
    ordering = ['name']

    def column_display(self, obj):
        if obj.column:
            return f"{obj.column.columns[:30]}"
        return "N/A"

    column_display.short_description = 'Столбец'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'column__table__schema__base', 'name'
        )


# --- Связи и отношения ---
@admin.register(LinkColumnColumn)
class LinkColumnColumnAdmin(BaseAdmin):
    """Админка для связей столбцов"""

    autocomplete_fields = ['main', 'sub', 'type']

    list_display = (
        'id',
        'main_full_path_display',
        'sub_full_path_display',
        'type_display',
        'created_at'
    )

    search_fields = (
        'main__columns', 'main__table__name', 'main__table__schema__schema', 'main__table__schema__base__name',
        'sub__columns', 'sub__table__name', 'sub__table__schema__schema', 'sub__table__schema__base__name',
        'type__name',
    )

    list_filter = ('type', 'created_at')
    list_select_related = ('main__table__schema__base', 'sub__table__schema__base', 'type')
    ordering = ['-created_at']

    fieldsets = (
        ('Основной столбец', {
            'fields': ('main',),
            'description': 'Начните вводить имя столбца, таблицы, схемы или базы данных'
        }),
        ('Связанный столбец (опционально)', {
            'fields': ('sub',),
            'description': 'Начните вводить имя столбца, таблицы, схемы или базы данных'
        }),
        ('Тип связи', {
            'fields': ('type',),
        }),
    )

    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        """Оптимизируем запросы"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'main__table__schema__base',
            'sub__table__schema__base',
            'type'
        )

    def main_full_path_display(self, obj):
        """Отображаем полный путь для основного столбца"""
        if obj.main:
            return format_full_path(obj.main, color='#1890ff')
        return "—"

    main_full_path_display.short_description = 'Основной столбец'

    def sub_full_path_display(self, obj):
        """Отображаем полный путь для связанного столбца"""
        if obj.sub:
            return format_full_path(obj.sub, color='#52c41a')
        return "—"

    sub_full_path_display.short_description = 'Связанный столбец'

    def type_display(self, obj):
        return obj.type.name if obj.type else "—"

    type_display.short_description = 'Тип связи'
    type_display.admin_order_field = 'type__name'


# --- Служебные модели ---
@admin.register(TotalData)
class TotalDataAdmin(BaseAdmin):
    """Админка для общих данных"""
    list_display = (
        'hash_address', 'stand', 'table_catalog', 'table_schema',
        'table_name', 'column_name', 'created_at'
    )
    list_filter = ('table_catalog', 'table_schema', 'table_type')
    search_fields = ('table_name__istartswith', 'column_name__istartswith')
    readonly_fields = ('hash_address', 'created_at', 'updated_at')
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('stand')
