# app_updates/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import DimUpdateMethod, LinkUpdateCol


@admin.register(DimUpdateMethod)
class DimUpdateMethodAdmin(admin.ModelAdmin):
    """Админка для методов обновления"""
    list_display = ['name', 'schedule', 'url']
    list_filter = ['schedule']

    # Поиск по полям CharField
    search_fields = ['name__icontains', 'schedule__icontains']

    # Автодополнение для ForeignKey
    autocomplete_fields = ['url']

    # Оптимизация
    list_per_page = 20
    list_select_related = ['url']


@admin.register(LinkUpdateCol)
class LinkUpdateColAdmin(admin.ModelAdmin):
    """Админка для связи столбцов"""
    list_display = ['type', 'get_main_display', 'get_sub_display']
    list_filter = ['type']

    # ПРАВИЛЬНЫЙ поиск:
    # - type__name: DimUpdateMethod.name (CharField)
    # - main__columns: LinkColumn.columns (CharField)
    # - sub__columns: LinkColumn.columns (CharField)
    search_fields = [
        'type__name__icontains',
        'main__columns__icontains',
        'sub__columns__icontains'
    ]

    # Автодополнение для всех ForeignKey
    autocomplete_fields = ['type', 'main', 'sub']

    # Оптимизация
    list_per_page = 20
    list_select_related = ['type', 'main', 'sub']

    # Кастомное отображение для лучшей читаемости
    def get_main_display(self, obj):
        if obj.main:
            url = reverse('admin:app_dbm_linkcolumn_change', args=[obj.main.id])
            return format_html('<a href="{}">{}</a>', url, obj.main)
        return "-"

    get_main_display.short_description = "Main Column"
    get_main_display.admin_order_field = "main__columns"

    def get_sub_display(self, obj):
        if obj.sub:
            url = reverse('admin:app_dbm_linkcolumn_change', args=[obj.sub.id])
            return format_html('<a href="{}">{}</a>', url, obj.sub)
        return "-"

    get_sub_display.short_description = "Sub Column"
    get_sub_display.admin_order_field = "sub__columns"