from django.contrib import admin
from .models import DimUpdateMethod, LinkUpdate, LinkColumnUpdate


@admin.register(DimUpdateMethod)
class DimUpdateMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(LinkUpdate)
class LinkUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', 'schedule', 'link_code')
    search_fields = ('schedule', 'link_code')
    list_filter = ('method',)
    ordering = ('id',)


@admin.register(LinkColumnUpdate)
class LinkColumnUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'update', 'main', 'sub')
    raw_id_fields = ('update', 'main', 'sub')
