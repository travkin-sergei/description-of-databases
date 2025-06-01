from django.contrib import admin
from .models import (
    Asset, AssetType, AssetDomain, AssetDetails,
   # AssetColumn, AssetCategory, AssetCategoryRelation, AssetColumnType
)


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = 'created_at', 'updated_at',
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return self.readonly_fields

#
# class AssetColumnInline(admin.TabularInline):
#     model = AssetColumn
#     extra = 1
#     fields = 'number', 'name', 'data_type', 'description', 'is_nullable', 'is_active',
#     verbose_name = "Столбец"
#     verbose_name_plural = "Столбцы"

#
# class AssetCategoryRelationInline(admin.TabularInline):
#     model = AssetCategoryRelation
#     extra = 1
#     fields = 'category', 'is_active',
#     verbose_name = "Связь с категорией"
#     verbose_name_plural = "Связи с категориями"


@admin.register(AssetType)
class AssetTypeAdmin(BaseAdmin):
    list_display = 'name', 'description', 'is_active',
    search_fields = 'name', 'description',
    list_editable = 'is_active',


@admin.register(AssetDomain)
class AssetDomainAdmin(BaseAdmin):
    list_display = 'name', 'description', 'res_url', 'is_active',
    search_fields = 'name', 'description', 'res_url',
    list_editable = 'is_active',


@admin.register(AssetDetails)
class AssetDetailsAdmin(BaseAdmin):
    list_display = 'name', 'description', 'is_active'
    search_fields = 'name', 'description',
    list_editable = 'is_active',
#
#
# @admin.register(Asset)
# class AssetAdmin(BaseAdmin):
#     inlines = [AssetColumnInline, AssetCategoryRelationInline]
#
#     list_display = 'type', 'domain', 'details', 'version', 'res_url', 'is_active',
#     list_select_related = 'type', 'domain', 'details',
#     search_fields = 'version', 'res_url', 'description', 'type__name', 'domain__name', 'details__name'
#     list_filter = 'type', 'domain', 'details', 'is_active',
#     autocomplete_fields = ['type', 'domain', 'details', ]


# @admin.register(AssetColumnType)
# class AssetColumnTypeAdmin(BaseAdmin):
#     """Типы данных."""
#
#     list_display = 'data_type',
#     search_fields = 'data_type',

#
# @admin.register(AssetColumn)
# class AssetColumnAdmin(BaseAdmin):
#     list_display = 'asset', 'name', 'data_type', 'is_nullable', 'is_active',
#     list_select_related = 'asset',
#     search_fields = 'name', 'data_type', 'description', 'asset__version', 'asset__type__name'
#     list_filter = 'asset', 'data_type', 'is_nullable', 'is_active',
#     autocomplete_fields = ['asset', ]

#
# @admin.register(AssetCategory)
# class AssetCategoryAdmin(BaseAdmin):
#     inlines = [AssetCategoryRelationInline]
#
#     list_display = 'name', 'description', 'is_active',
#     search_fields = 'name', 'description',
#     list_editable = 'is_active',

#
# @admin.register(AssetCategoryRelation)
# class AssetCategoryRelationAdmin(BaseAdmin):
#     list_display = 'asset', 'category', 'is_active',
#     list_select_related = 'asset', 'category',
#     search_fields = 'asset__version', 'category__name'
#     list_filter = 'category', 'is_active',
#     autocomplete_fields = ['asset', 'category', ]
