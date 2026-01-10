# app_doc/admin.py
from django.contrib import admin
from .models import DimDocType, DimDoc


@admin.register(DimDocType)
class DimDocTypeAdmin(admin.ModelAdmin):
    """001 Тип документа"""

    list_display = ('id', 'name', 'description',)
    list_display_links = ('id', 'name',)
    search_fields = ('name', 'description',)
    ordering = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('dimdoc_set')


@admin.register(DimDoc)
class DimDocAdmin(admin.ModelAdmin):
    list_display = ('id', 'doc_type', 'number', 'date_start', 'date_stop', 'is_active', 'link')
    list_display_links = ('id', 'number')
    list_filter = ('doc_type', 'date_start', 'date_stop')
    search_fields = ('number', 'description', 'link__url')
    ordering = ('-date_start', 'number')
    autocomplete_fields = ('doc_type', 'link')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            'Системные поля', {
                'fields': ('created_at', 'updated_at', 'is_active',),
                'classes': ('collapse',)
            }
        ), (
            'Основная информация', {
                'fields': ('doc_type', 'number', 'date_start', 'date_stop', 'description', 'link',)
            }
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doc_type', 'link')
