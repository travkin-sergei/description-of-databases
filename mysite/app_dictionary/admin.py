from django.contrib import admin
from .models import DimCategory, DimDictionary, LinkDictionaryName


@admin.register(DimCategory)
class DimCategoryAdmin(admin.ModelAdmin):
    """Настройка администратора для модели DimCategory."""

    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_editable = ('is_active',)
    list_per_page = 20


class LinkDictionaryNameInline(admin.TabularInline):
    """Inline-форма для синонимов словаря."""
    model = LinkDictionaryName
    extra = 1  # Количество пустых форм по умолчанию
    fields = ('synonym',)
    verbose_name = 'Синоним'
    verbose_name_plural = 'Синонимы'


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
    inlines = [LinkDictionaryNameInline]  # Вставка синонимов

    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'is_active')
        }),
        ('Дополнительные параметры', {
            'classes': ('collapse',),
            'fields': ('description',),
        }),
    )
