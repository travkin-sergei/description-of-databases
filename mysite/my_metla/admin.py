from django.contrib import admin
from django.db.models import Q
from .models import (
    Environment,
    BaseName,
    BaseType,
    Base,
    SchemAlias,
    SchemesName,
    Schemas,
    TableType,
    TableName,
    SchemaTable,
    ColumnType,
    ColumnName,
    Column,
)


# ========== Базовые модели (без изменений) ==========
@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(BaseName)
class BaseNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(BaseType)
class BaseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(SchemAlias)
class SchemAliasAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(SchemesName)
class SchemesNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(TableType)
class TableTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(TableName)
class TableNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ColumnType)
class ColumnTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ColumnName)
class ColumnNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


# ========== Модели с контекстным поиском ==========
class BaseInline(admin.TabularInline):
    model = Base
    extra = 0
    fields = ('name', 'type', 'host_name', 'host', 'port', 'version', 'is_active')
    show_change_link = True
    autocomplete_fields = ('name', 'type')


@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'host_name', 'host', 'port', 'version', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name__name', 'host', 'port', 'host_name')
    autocomplete_fields = ('name', 'type')


class SchemasInline(admin.TabularInline):
    model = Schemas
    extra = 0
    fields = ('base', 'schema', 'alias', 'env', 'is_active')
    show_change_link = True
    autocomplete_fields = ('base', 'schema', 'alias', 'env')


@admin.register(Schemas)
class SchemasAdmin(admin.ModelAdmin):
    list_display = ('base', 'schema', 'alias', 'env', 'is_active')
    list_filter = ('env', 'is_active')
    search_fields = ('base__host_name', 'schema__name', 'alias__name', 'env__name')
    autocomplete_fields = ('base', 'schema', 'alias', 'env')

    # Контекстный поиск: при выборе `base` фильтруем доступные `SchemesName`
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if 'base' in request.GET:
            base_id = request.GET['base']
            queryset = queryset.filter(base__id=base_id)

        return queryset, use_distinct


class SchemaTableInline(admin.TabularInline):
    model = SchemaTable
    extra = 0
    fields = ('schemas', 'table', 'table_type', 'table_is_metadata', 'is_active')
    show_change_link = True
    autocomplete_fields = ('schemas', 'table', 'table_type')


@admin.register(SchemaTable)
class SchemaTableAdmin(admin.ModelAdmin):
    list_display = ('schemas', 'table', 'table_type', 'table_is_metadata', 'is_active')
    list_filter = ('table_type', 'table_is_metadata', 'is_active')
    search_fields = ('table__name', 'schemas__schema__name', 'schemas__base__host_name')
    autocomplete_fields = ('schemas', 'table', 'table_type')

    # Контекстный поиск: при выборе `schemas` фильтруем доступные `TableName`
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if 'schemas' in request.GET:
            schemas_id = request.GET['schemas']
            queryset = queryset.filter(schemas__id=schemas_id)

        return queryset, use_distinct


class ColumnInline(admin.TabularInline):
    model = Column
    extra = 0
    fields = ('numbers', 'name', 'type', 'is_nullable', 'is_auto', 'is_active')
    ordering = ('numbers',)
    autocomplete_fields = ('name', 'type', 'table')


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('table', 'numbers', 'name', 'type', 'is_nullable', 'is_auto', 'is_active')
    list_filter = ('type', 'is_nullable', 'is_auto', 'is_active')
    search_fields = ('name__name', 'table__table__name', 'table__schemas__schema__name')
    ordering = ('table', 'numbers')
    autocomplete_fields = ('table', 'name', 'type')

    # Контекстный поиск: при выборе `table` фильтруем доступные `ColumnName`
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if 'table' in request.GET:
            table_id = request.GET['table']
            queryset = queryset.filter(table__id=table_id)

        return queryset, use_distinct