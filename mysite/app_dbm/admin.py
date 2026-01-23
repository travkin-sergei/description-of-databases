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


# ================== ОПТИМИЗИРОВАННАЯ АДМИНКА ДЛЯ LinkColumn ==================
@admin.register(LinkColumn)
class LinkColumnAdmin(BaseAdmin):
    """Админка для столбцов с улучшенным поиском"""

    # 🔍 ПОИСК ПО ВСЕМУ ПУТИ
    search_fields = (
        'columns',  # Имя столбца
        'table__name',  # Имя таблицы
        'table__schema__schema',  # Имя схемы
        'table__schema__base__name',  # Имя базы данных
        'type',  # Тип данных
    )

    # 📋 СПИСОК ЗАПИСЕЙ
    list_display = (
        'id',
        'full_path_display',
        'type',
        'is_key',
        'is_null',
        'created_at'
    )

    # ⚙️ ФИЛЬТРЫ
    list_filter = ('is_key', 'is_null', 'table__schema__base')

    # 📄 ПОЛЯ В ФОРМЕ РЕДАКТИРОВАНИЯ
    fields = ('table', 'columns', 'type', 'is_null', 'is_key',
              'unique_together', 'default', 'description', 'stage')

    def full_path_display(self, obj):
        """Отображаем полный путь столбца"""
        try:
            base = obj.table.schema.base.name if obj.table.schema.base else '???'
            schema = obj.table.schema.schema if obj.table.schema else '???'
            table = obj.table.name if obj.table else '???'
            column = obj.columns

            return format_html(
                '<div style="font-family: monospace; font-size: 11px; line-height: 1.3;">'
                '<span style="color: #666;">{}.{}.{}.</span>'
                '<span style="color: #1890ff; font-weight: bold;">{}</span>'
                '</div>',
                base, schema, table, column
            )
        except AttributeError:
            return str(obj)[:50]

    full_path_display.short_description = 'Полный путь столбца'

    def get_queryset(self, request):
        """Оптимизируем запросы"""
        return super().get_queryset(request).select_related(
            'table__schema__base'
        )


# ================== РЕГИСТРАЦИЯ МОДЕЛЕЙ ДЛЯ AUTOCOMPLETE ==================


@admin.register(DimStage)
class DimStageAdmin(BaseAdmin):
    """Админка для стендов"""
    list_display = ('name', 'description')
    search_fields = ('name__istartswith',)


@admin.register(DimTypeLink)
class DimTypeLinkAdmin(BaseAdmin):
    """Админка для типов связей"""
    list_display = ('name',)
    search_fields = ('name__istartswith',)


# ================== ОСНОВНАЯ АДМИНКА ДЛЯ LinkColumnColumn ==================
@admin.register(LinkColumnColumn)
class LinkColumnColumnAdmin(BaseAdmin):
    """Админка для связей столбцов с автокомплитом"""

    # 🎯 АВТОКОМПЛИТ ПОЛЯ
    autocomplete_fields = ['main', 'sub', 'type']

    # 📋 СПИСОК ЗАПИСЕЙ
    list_display = (
        'id',
        'main_full_path_display',
        'sub_full_path_display',
        'type_display',
        'created_at'
    )

    # 🔍 ПОИСК
    search_fields = (
        'main__columns',
        'main__table__name',
        'main__table__schema__schema',
        'main__table__schema__base__name',
        'sub__columns',
        'sub__table__name',
        'sub__table__schema__schema',
        'sub__table__schema__base__name',
        'type__name',
    )

    # ⚙️ ФИЛЬТРЫ
    list_filter = ('type', 'created_at')

    # 📄 ПОЛЯ В ФОРМЕ РЕДАКТИРОВАНИЯ
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
            try:
                base = obj.main.table.schema.base.name if obj.main.table.schema.base else '???'
                schema = obj.main.table.schema.schema if obj.main.table.schema else '???'
                table = obj.main.table.name if obj.main.table else '???'
                column = obj.main.columns

                return format_html(
                    '<div style="font-family: monospace; font-size: 11px; line-height: 1.3;">'
                    '<span style="color: #666;">{}.{}.{}.</span>'
                    '<span style="color: #1890ff; font-weight: bold;">{}</span>'
                    '</div>',
                    base, schema, table, column
                )
            except AttributeError:
                return str(obj.main)[:50]
        return "—"

    main_full_path_display.short_description = 'Основной столбец'

    def sub_full_path_display(self, obj):
        """Отображаем полный путь для связанного столбца"""
        if obj.sub:
            try:
                base = obj.sub.table.schema.base.name if obj.sub.table.schema.base else '???'
                schema = obj.sub.table.schema.schema if obj.sub.table.schema else '???'
                table = obj.sub.table.name if obj.sub.table else '???'
                column = obj.sub.columns

                return format_html(
                    '<div style="font-family: monospace; font-size: 11px; line-height: 1.3;">'
                    '<span style="color: #666;">{}.{}.{}.</span>'
                    '<span style="color: #52c41a; font-weight: bold;">{}</span>'
                    '</div>',
                    base, schema, table, column
                )
            except AttributeError:
                return str(obj.sub)[:50]
        return "—"

    sub_full_path_display.short_description = 'Связанный столбец'

    def type_display(self, obj):
        return obj.type.name if obj.type else "—"

    type_display.short_description = 'Тип связи'


# ================== RAW_ID_FIELDS ВЕРСИЯ (ЕСЛИ НУЖНО) ==================
class LinkColumnColumnRawIdAdmin(BaseAdmin):
    """Админка с raw_id_fields"""

    raw_id_fields = ['main', 'sub']
    autocomplete_fields = ['type']

    list_display = (
        'id',
        'main_info',
        'sub_info',
        'type',
        'created_at'
    )

    fields = ('main', 'sub', 'type', 'created_at')
    readonly_fields = ('created_at',)

    def main_info(self, obj):
        if obj.main:
            try:
                return f"{obj.main.columns} (ID: {obj.main.id})"
            except:
                return f"ID: {obj.main.id}"
        return "—"

    main_info.short_description = 'Основной столбец'

    def sub_info(self, obj):
        if obj.sub:
            try:
                return f"{obj.sub.columns} (ID: {obj.sub.id})"
            except:
                return f"ID: {obj.sub.id}"
        return "—"

    sub_info.short_description = 'Связанный столбец'


class LinkColumnInline(admin.TabularInline):
    model = LinkColumn
    extra = 0  # Не добавлять пустые формы по умолчанию
    fields = ('columns', 'type', 'is_key', 'is_null', 'description')
    show_change_link = True  # Позволяет перейти к полной форме редактирования


# ================== ОСТАЛЬНЫЕ МОДЕЛИ ==================
@admin.register(TotalData)
class TotalDataAdmin(BaseAdmin):
    list_display = ('hash_address', 'stand', 'table_catalog', 'table_schema',
                    'table_name', 'column_name', 'created_at')
    list_filter = ('table_catalog', 'table_schema', 'table_type')
    search_fields = ('table_name__istartswith', 'column_name__istartswith')
    readonly_fields = ('hash_address', 'created_at', 'updated_at')


@admin.register(DimDB)
class DimDBAdmin(BaseAdmin):
    list_display = ('name', 'version', 'description')
    search_fields = ('name__istartswith', 'version__istartswith')


@admin.register(LinkDB)
class LinkDBAdmin(BaseAdmin):
    list_display = ('name', 'alias', 'host', 'port', 'stage', 'base')
    list_filter = ('stage', 'base')
    search_fields = ('name__istartswith', 'alias__istartswith')


@admin.register(LinkSchema)
class LinkSchemaAdmin(BaseAdmin):
    list_display = ('schema', 'base', 'description')
    list_filter = ('base',)
    search_fields = ('schema__istartswith',)


@admin.register(DimTableType)
class DimTableTypeAdmin(BaseAdmin):
    list_display = ('name', 'description')
    search_fields = ('name__istartswith',)


@admin.register(DimColumnName)
class DimColumnNameAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name__istartswith',)
    list_per_page = 200


@admin.register(DimTableNameType)
class DimTableNameTypeAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name__istartswith',)


@admin.register(LinkTableName)
class LinkTableNameAdmin(BaseAdmin):
    list_display = ('name', 'table', 'type', 'is_publish')
    list_filter = ('type', 'is_publish')
    search_fields = ('name__istartswith', 'table__name__istartswith')


@admin.register(LinkColumnName)
class LinkColumnNameAdmin(BaseAdmin):
    list_display = ('name', 'column_display')
    search_fields = ('name__name__istartswith', 'column__columns__istartswith')

    def column_display(self, obj):
        if obj.column:
            return f"{obj.column.columns[:30]}"
        return "N/A"

    column_display.short_description = 'Столбец'


@admin.register(LinkTable)
class LinkTableAdmin(BaseAdmin):
    """Админка для таблиц"""
    list_display = ('name', 'schema_display', 'type', 'is_metadata')
    search_fields = ('name__istartswith', 'schema__schema__istartswith')
    inlines = [LinkColumnInline]  # ← Добавлено

    def schema_display(self, obj):
        return f"{obj.schema.base.name}.{obj.schema.schema}"

    schema_display.short_description = 'Схема'
