from django.contrib import admin
from .models import *

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('code', 'name')

@admin.register(BaseGroup)
class BaseGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_catalog', 'is_active', 'created_at', 'updated_at')
    search_fields = ('table_catalog',)

@admin.register(StageType)
class StageTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'base', 'type', 'host_db', 'host_name', 'version', 'is_active')
    list_filter = ('type', 'base')
    search_fields = ('host_db',)

@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'base', 'table_schema', 'comment', 'is_active')
    search_fields = ('table_schema', 'comment')
    autocomplete_fields = ['base']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_name', 'schema', 'type', 'is_metadata', 'is_active')
    list_filter = ('type', 'is_metadata', 'schema')
    search_fields = ('table_name', 'table_com')
    filter_horizontal = ('tablenames',)
    autocomplete_fields = ['schema', 'tablenames']

@admin.register(TableName)
class TableNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'table', 'language', 'is_active')
    search_fields = ('name',)
    autocomplete_fields = ['table', 'language']

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'column_name', 'data_type', 'is_nullable', 'is_auto', 'is_active')
    search_fields = ('column_name',)
    list_filter = ('data_type',)
    autocomplete_fields = ['table']

@admin.register(ColumnMDType)
class ColumnMDTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'md_type', 'is_active')
    search_fields = ('md_type',)

@admin.register(StageColumn)
class StageColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage', 'column', 'is_active')
    search_fields = ('stage__host_db', 'column__column_name')
    autocomplete_fields = ['stage', 'column']

@admin.register(ColumnColumn)
class ColumnColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'main', 'sub', 'type', 'update', 'is_active')
    list_filter = ('type',)
    autocomplete_fields = ['main', 'sub', 'update']

@admin.register(UpdateMethod)
class UpdateMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', 'is_active')
    search_fields = ('method',)

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'schedule', 'method', 'is_active')
    search_fields = ('name', 'type')
    list_filter = ('type',)
    autocomplete_fields = ['method']

@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'name_fun', 'is_active')
    search_fields = ('name_fun',)
    autocomplete_fields = ['schema']

@admin.register(StageFunction)
class StageFunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage', 'function', 'is_active')
    autocomplete_fields = ['stage', 'function']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'is_active')
    search_fields = ('service',)

@admin.register(ServiceTable)
class ServiceTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'table', 'is_active')
    search_fields = ('service__service', 'table__table_name')
    autocomplete_fields = ['service', 'table']
