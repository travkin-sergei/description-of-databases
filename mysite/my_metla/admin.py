from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Lower

from .models import (
    ColumnName, Environment,
    ColumnType, TableName,
    TableType, SchemaName, Base, BaseName,
    BaseSchemeAlias, BaseType,
    TableColumn, SchemaTable, BaseSchema,
)


class BaseAdminWithSearch(ModelAdmin):
    """Базовый класс админки с улучшенным поиском"""

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if not hasattr(self.model, 'name'):
            return queryset, use_distinct

        try:
            # Приоритет для имен, начинающихся с search_term (регистронезависимо)
            queryset = queryset.annotate(
                search_priority=Case(
                    When(name__istartswith=search_term, then=0),
                    When(name__icontains=search_term, then=1),
                    default=2,
                    output_field=IntegerField()
                ),
                lower_name=Lower('name')
            ).order_by('search_priority', 'lower_name')
        except:
            pass

        return queryset, use_distinct


class SchemaTableInline(TabularInline):
    model = SchemaTable
    extra = 0
    autocomplete_fields = 'table_type', 'alias',
    raw_id_fields = 'table',
    # classes = 'collapse',
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


class TableColumnInline(TabularInline):
    model = TableColumn
    extra = 0
    raw_id_fields = ('name', 'type')
    # classes = ('collapse',)


# Основные админки
@admin.register(Environment)
class EnvironmentAdmin(BaseAdminWithSearch):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(BaseSchemeAlias)
class BaseSchemeAliasAdmin(BaseAdminWithSearch):
    list_display = ('id', 'base', 'schema', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'base', 'schema',)
    list_filter = ('is_active',)
    search_fields = ('base', 'schema',)
    ordering = ('base', 'schema',)


@admin.register(BaseType)
class BaseTypeAdmin(BaseAdminWithSearch):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(BaseName)
class BaseNameAdmin(BaseAdminWithSearch):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(SchemaName)
class SchemaNameAdmin(BaseAdminWithSearch):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Base)
class TableTypeAdmin(BaseAdminWithSearch):
    list_display = ('id', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id',)
    list_filter = ('is_active',)
    search_fields = ('is_active',)
    ordering = ('is_active',)


@admin.register(TableType)
class TableTypeAdmin(BaseAdminWithSearch):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(TableName)
class TableNameAdmin(BaseAdminWithSearch):
    """Список таблиц и отнесение к базе и схеме данных"""

    inlines = [SchemaTableInline]

    list_display = ('id', 'created_at', 'updated_at', 'name', 'is_active')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ColumnType)
class ColumnTypeAdmin(BaseAdminWithSearch):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(BaseSchema)
class BaseSchemaAdmin(BaseAdminWithSearch):
    list_display = ('base', 'schema', 'alias', 'env',)
    list_display_links = ('base',)
    list_filter = ('is_active',)
    search_fields = ('schema',)
    ordering = ('schema',)


@admin.register(ColumnName)
class ColumnNameAdmin(BaseAdminWithSearch):
    list_display = ('id', 'created_at', 'updated_at', 'name', 'is_active',)
    list_display_links = ('created_at', 'updated_at',)
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(SchemaTable)
class SchemaTableAdmin(ModelAdmin):
    inlines = [TableColumnInline]

    list_display = ('id', 'alias', 'table', 'table_type', 'table_is_metadata', 'is_active')
    list_display_links = ('id', 'alias')
    list_filter = ('table_type', 'table_is_metadata', 'is_active')
    search_fields = ('alias__name', 'table__name')
    raw_id_fields = ('alias', 'table', 'table_type')
    ordering = ('alias', 'table')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            queryset = queryset.annotate(
                search_priority=Case(
                    When(alias__name__istartswith=search_term, then=0),
                    When(alias__name__icontains=search_term, then=1),
                    When(table__name__istartswith=search_term, then=2),
                    When(table__name__icontains=search_term, then=3),
                    default=4,
                    output_field=IntegerField()
                ),
                lower_alias_name=Lower('alias__name'),
                lower_table_name=Lower('table__name')
            ).order_by('search_priority', 'lower_alias_name', 'lower_table_name')
        except:
            pass
        return queryset, use_distinct


@admin.register(TableColumn)
class TableColumnAdmin(ModelAdmin):
    list_display = ('id', 'schema_table', 'name', 'type', 'is_nullable', 'is_auto', 'numbers', 'is_active')
    list_display_links = ('id', 'schema_table')
    list_filter = ('type', 'is_nullable', 'is_auto', 'is_active')
    search_fields = ('schema_table__table__name', 'name__name')
    raw_id_fields = ('schema_table', 'name', 'type')
    ordering = ('schema_table', 'numbers')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            queryset = queryset.annotate(
                search_priority=Case(
                    When(name__name__istartswith=search_term, then=0),
                    When(name__name__icontains=search_term, then=1),
                    When(schema_table__table__name__istartswith=search_term, then=2),
                    When(schema_table__table__name__icontains=search_term, then=3),
                    default=4,
                    output_field=IntegerField()
                ),
                lower_name=Lower('name__name'),
                lower_table_name=Lower('schema_table__table__name')
            ).order_by('search_priority', 'lower_name', 'lower_table_name')
        except:
            pass
        return queryset, use_distinct
