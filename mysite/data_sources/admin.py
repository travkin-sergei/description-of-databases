from django.contrib import admin

from .models import DataSources


@admin.register(DataSources)
class DataSourcesAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'name_sources',)
    search_fields = ('created_at', 'is_active', 'name_sources',)
