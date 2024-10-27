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


class BaseGroupAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'table_catalog',)
    search_fields = ('created_at', 'is_active', 'table_catalog',)


admin.site.register(BaseGroup, BaseGroupAdmin)


class SchemaAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'base', 'table_schema',)
    search_fields = ('created_at', 'is_active', 'table_schema',)


admin.site.register(Schema, SchemaAdmin)


class TableAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'is_metadata', 'schema', 'table_name',)
    search_fields = ('created_at', 'is_active', 'is_metadata', 'table_name',)


admin.site.register(Table, TableAdmin)


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'table', 'column_name',)
    search_fields = ('created_at', 'is_active', 'column_name',)


admin.site.register(Column, ColumnAdmin)


class BaseAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'base', 'host_name', 'host_db', 'version', 'type')
    search_fields = ('created_at', 'is_active', 'host_name',)


admin.site.register(Base, BaseAdmin)


class StageColumnAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'hash_address',)
    search_fields = ('created_at', 'is_active', 'hash_address',)


admin.site.register(StageColumn, StageColumnAdmin)


class ColumnColumnAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'hash_address',)
    search_fields = ('created_at', 'is_active', 'hash_address',)


admin.site.register(ColumnColumn, ColumnColumnAdmin)


class UpdateMethodAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'method',)
    search_fields = ('created_at', 'is_active', 'method',)


admin.site.register(UpdateMethod, UpdateMethodAdmin)


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'name', 'type', 'method', 'schedule',)
    search_fields = ('created_at', 'is_active', 'name',)


admin.site.register(Update, UpdateAdmin)


class FunctionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'name_fun',)
    search_fields = ('created_at', 'is_active', 'name_fun',)


admin.site.register(Function, FunctionAdmin)


class StageFunctionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active',)
    search_fields = ('created_at', 'is_active',)


admin.site.register(StageFunction, StageFunctionAdmin)


class StageTypeAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'name')
    search_fields = ('created_at', 'is_active', 'name')


admin.site.register(StageType, StageTypeAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'service',)
    search_fields = ('created_at', 'is_active', 'service',)


admin.site.register(Service, ServiceAdmin)


class ServiceTableAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'service', 'table',)
    search_fields = ('created_at', 'is_active',)


admin.site.register(ServiceTable, ServiceTableAdmin)
