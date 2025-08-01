from django.contrib import admin
from .models import DimCategory, DimDictionary


@admin.register(DimCategory)
class DimCategoryAdmin(admin.ModelAdmin):
    """Настройка администратора для модели DimCategory."""

    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_editable = ('is_active',)
    list_per_page = 20


@admin.register(DimDictionary)
class DimDictionaryAdmin(admin.ModelAdmin):
    """Конфигурация администратора для модели DimDictionary."""

    list_display = ('name', 'category', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_editable = ('is_active',)
    list_per_page = 20
    raw_id_fields = ('category',)
    autocomplete_fields = ('category',)

    # If you want to show description in the admin form
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'is_active')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('description',),
        }),
    )
