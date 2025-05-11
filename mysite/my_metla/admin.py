from django.contrib import admin
from .models import (
    BaseType, Base, Schema, TableType, Table,
    ColumnType, Column, BaseSchema, SchemaTable, TableColumn
)

# ------------------------
# Базовые типы (справочники)
# ------------------------

@admin.register(BaseType)
class BaseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(TableType)
class TableTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(ColumnType)
class ColumnTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)

# ------------------------
# Inlines для связей
# ------------------------

class SchemaToBaseInline(admin.TabularInline):
    """Связь схем с базой"""
    model = BaseSchema
    extra = 1
    autocomplete_fields = ['schema']
    fields = ('schema', 'description', 'is_active')
    verbose_name = "Привязанная схема"
    verbose_name_plural = "Привязанные схемы"

class TableToBaseSchemaInline(admin.TabularInline):
    """Связь таблиц с BaseSchema"""
    model = SchemaTable
    extra = 1
    autocomplete_fields = ['table', 'table_type']
    fields = ('table', 'table_type', 'table_is_metadata', 'description', 'is_active')
    verbose_name = "Таблица в схеме"
    verbose_name_plural = "Таблицы в схеме"

class ColumnToSchemaTableInline(admin.TabularInline):
    """Связь столбцов с SchemaTable"""
    model = TableColumn
    extra = 1
    autocomplete_fields = ['column']
    fields = ('column', 'numbers', 'description', 'is_active')
    verbose_name = "Столбец таблицы"
    verbose_name_plural = "Столбцы таблицы"

# ------------------------
# Основные модели с вложенностью
# ------------------------

@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    inlines = [SchemaToBaseInline]  # Уровень 1: Схемы к базе
    list_display = ('name', 'host', 'port', 'type', 'is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('name', 'host')
    list_filter = ('type', 'is_active')
    autocomplete_fields = ['type']

@admin.register(BaseSchema)
class BaseSchemaAdmin(admin.ModelAdmin):
    inlines = [TableToBaseSchemaInline]  # Уровень 2: Таблицы к BaseSchema
    list_display = ('base', 'schema', 'is_active', 'created_at')
    list_editable = ('is_active',)
    autocomplete_fields = ['base', 'schema']
    search_fields = ('base__name', 'schema__name')
    list_filter = ('base__type', 'is_active')

@admin.register(SchemaTable)
class SchemaTableAdmin(admin.ModelAdmin):
    inlines = [ColumnToSchemaTableInline]  # Уровень 3: Столбцы к SchemaTable
    list_display = ('base_schema', 'table', 'table_type', 'table_is_metadata', 'is_active')
    list_editable = ('table_is_metadata', 'is_active')
    autocomplete_fields = ['base_schema', 'table', 'table_type']
    search_fields = ('table__name', 'base_schema__schema__name')
    list_filter = ('table_type', 'table_is_metadata', 'is_active')

# ------------------------
# Остальные модели
# ------------------------

@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_nullable', 'is_auto', 'is_active')
    list_editable = ('is_nullable', 'is_auto', 'is_active')
    autocomplete_fields = ['type']
    search_fields = ('name',)
    list_filter = ('type', 'is_nullable', 'is_auto', 'is_active')

@admin.register(TableColumn)
class TableColumnAdmin(admin.ModelAdmin):
    list_display = ('schema_table', 'column', 'numbers', 'is_active')
    list_editable = ('numbers', 'is_active')
    autocomplete_fields = ['schema_table', 'column']
    search_fields = ('column__name', 'schema_table__table__name')
    list_filter = ('is_active',)