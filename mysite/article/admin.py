from django.contrib import admin

from .models import Article


@admin.register(Article)
class DataSourcesAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_active', 'title', 'content',)
    search_fields = ('created_at', 'is_active', 'title', 'content',)
