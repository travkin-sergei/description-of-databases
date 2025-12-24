from django.contrib import admin
from .models import ColumnGroupName, ColumnGroup


@admin.register(ColumnGroupName)
class ColumnGroupNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)

    verbose_name = 'Группировки'
    verbose_name_plural = 'Группировки'


@admin.register(ColumnGroup)
class ColumnGroupAdmin(admin.ModelAdmin):
    list_display = ('column', 'group_name', 'created_at', 'updated_at', 'is_active')
    raw_id_fields = ('column', 'group_name',)
    search_fields = ('column__name', 'group_name',)
    list_filter = ('is_active', 'group_name',)
    ordering = ('column', 'group_name',)

    verbose_name = 'Столбец и Закон'
    verbose_name_plural = 'Столбцы и Законы'
