from django.contrib import admin
from .models import (
    BaseGroup,
    Schema,
    Table,
    Column,
    Base,
    StageColumn,
    ColumnColumn,
    Update,
    UpdateMethod,
    Function,
    StageFunction,
    StageType,
    Service,
    ServiceTable,
)


@admin.register(BaseGroup)
class BaseGroupAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'table_catalog',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'table_catalog',)
    readonly_fields = ('hash_address',)

@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'base', 'table_schema',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'table_schema',)
    readonly_fields = ('hash_address',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'is_metadata', 'schema', 'table_name',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'is_metadata', 'table_name',)
    readonly_fields = ('hash_address',)

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'table', 'column_name',)
    search_fields = ('created_at', 'is_active', 'column_name',)
    readonly_fields = ('hash_address',)

@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'base', 'host_name', 'host_db', 'version', 'type')
    search_fields = ('hash_address', 'created_at', 'is_active', 'host_name',)
    readonly_fields = ('hash_address',)

@admin.register(StageColumn)
class StageColumnAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'hash_address',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'hash_address',)
    readonly_fields = ('hash_address',)

@admin.register(ColumnColumn)
class ColumnColumnAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'hash_address',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'hash_address',)
    readonly_fields = ('hash_address',)

@admin.register(UpdateMethod)
class UpdateMethodAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'method',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'method',)


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'name', 'type', 'method', 'schedule',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'name',)
    readonly_fields = ('hash_address',)

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'name_fun',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'name_fun',)
    readonly_fields = ('hash_address',)

@admin.register(StageFunction)
class StageFunctionAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active',)
    search_fields = ('hash_address', 'created_at', 'is_active',)


@admin.register(StageType)
class StageTypeAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'name')
    search_fields = ('hash_address', 'created_at', 'is_active', 'name')
    readonly_fields = ('hash_address',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'service',)
    search_fields = ('hash_address', 'created_at', 'is_active', 'service',)
    readonly_fields = ('hash_address',)

@admin.register(ServiceTable)
class ServiceTableAdmin(admin.ModelAdmin):
    list_display = ('hash_address', 'created_at', 'is_active', 'service', 'table',)
    search_fields = ('hash_address', 'created_at', 'is_active',)
    readonly_fields = ('hash_address',)