from django.contrib import admin
from .models import DimUpdateMethod, LinkUpdate

class LinkUpdateInline(admin.TabularInline):
    model = LinkUpdate
    extra = 0
    fields = ('column',)
    verbose_name = 'Связь столбцов'
    verbose_name_plural = 'Связи столбцов'
    raw_id_fields = ('column',)  # Полезно, если связей много

@admin.register(DimUpdateMethod)
class DimUpdateMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'schedule', 'link_code')
    search_fields = ('name', 'schedule')
    list_filter = ('schedule',)
    fields = ('name', 'schedule', 'link_code')
    inlines = [LinkUpdateInline]

@admin.register(LinkUpdate)
class LinkUpdateAdmin(admin.ModelAdmin):
    list_display = ('name', 'column')
    list_filter = ('name',)
    search_fields = ('name__name', 'column__column_source__name', 'column__column_target__name')
    raw_id_fields = ('column',)  # Для удобства выбора при большом количестве связей
    autocomplete_fields = ['name']  # Включаем автодополнение для поля name