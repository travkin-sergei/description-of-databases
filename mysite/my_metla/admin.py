from django.contrib import admin
from .models import (
    Environment, BaseName, SchemaName, ColumnName,
    BaseType, Base, TableType, Table,
    ColumnType, BaseSchema, Column, SchemaTable, TableColumn,
)


# ------------------------
# Остальные модели
# ------------------------

@admin.register(BaseName)
class BaseNameAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'type', 'is_nullable', 'is_auto', 'is_active')
    list_editable = ('is_nullable', 'is_auto', 'is_active')
    autocomplete_fields = ['type']
    search_fields = ('name',)
    list_filter = ('type', 'is_nullable', 'is_auto', 'is_active')
    readonly_fields = 'hash_address',


# ------------------------
# Базовые типы (справочники)
# ------------------------

@admin.register(BaseType)
class BaseTypeAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


@admin.register(TableType)
class TableTypeAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


@admin.register(ColumnType)
class ColumnTypeAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


# ------------------------
# Модели для автозаполнения
# ------------------------

@admin.register(SchemaName)
class SchemaNameAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


@admin.register(ColumnName)
class ColumnNameAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = 'hash_address',


# ------------------------
# Inlines для связей
# ------------------------

class SchemaToBaseInline(admin.TabularInline):
    model = BaseSchema
    extra = 0
    autocomplete_fields = ['schema']
    fields = ('hash_address','schema', 'description', 'is_active')
    verbose_name = "Привязанная схема"
    verbose_name_plural = "Привязанные схемы"
    readonly_fields = 'hash_address',


class TableToBaseSchemaInline(admin.TabularInline):
    model = SchemaTable
    extra = 0
    autocomplete_fields = ['table', 'table_type']
    fields = ('hash_address','table', 'table_type', 'table_is_metadata', 'description', 'is_active')
    verbose_name = "Таблица в схеме"
    verbose_name_plural = "Таблицы в схеме"
    readonly_fields = 'hash_address',


class ColumnToSchemaTableInline(admin.TabularInline):
    model = TableColumn
    extra = 0
    autocomplete_fields = ['name', 'type']
    fields = ('hash_address','numbers', 'name', 'type', 'is_nullable', 'is_auto', 'description', 'is_active')
    list_filter = ('is_nullable', 'is_auto')
    search_fields = ('name__name', 'type__name')
    readonly_fields = 'hash_address',


# ------------------------
# Основные модели с вложенностью
# ------------------------

@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('hash_address','name', 'host', 'port', 'type', 'is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('name', 'host')
    list_filter = ('type', 'is_active')
    autocomplete_fields = ['type']
    readonly_fields = 'hash_address',


@admin.register(BaseSchema)
class BaseSchemaAdmin(admin.ModelAdmin):
    list_display = ('hash_address','base', 'schema', 'is_active')
    list_editable = ('is_active',)
    autocomplete_fields = ['base', 'schema']
    search_fields = ('base__name', 'schema__name')
    readonly_fields = 'hash_address',


@admin.register(SchemaTable)
class SchemaTableAdmin(admin.ModelAdmin):
    inlines = [ColumnToSchemaTableInline]
    list_display = ('hash_address','base_schema', 'table', 'table_type', 'table_is_metadata', 'is_active')
    list_editable = ('table_is_metadata', 'is_active')
    autocomplete_fields = ['base_schema', 'table', 'table_type']
    search_fields = ('table__name', 'base_schema__schema__name')
    list_filter = ('table_type', 'table_is_metadata', 'is_active')
    readonly_fields = 'hash_address',
