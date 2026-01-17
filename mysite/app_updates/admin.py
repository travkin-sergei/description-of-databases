# app_updates/admin.py
from django.contrib import admin
from .models import DimUpdateMethod, LinkUpdateCol


@admin.register(DimUpdateMethod)
class DimUpdateMethodAdmin(admin.ModelAdmin):
    """Простая админка для методов обновления"""
    list_display = ['name', 'schedule', 'url']
    list_filter = ['schedule']
    search_fields = ['name', 'schedule', 'url__name']
    autocomplete_fields = ['url']


@admin.register(LinkUpdateCol)
class LinkUpdateColAdmin(admin.ModelAdmin):
    """Простая админка для связи столбцов"""


    list_display = ['type', 'main', 'sub']
    list_filter = ['type']
    search_fields = ['type__name', 'main__name', 'sub__name']

    # Автодополнение для всех ForeignKey
    autocomplete_fields = ['type', 'main', 'sub']