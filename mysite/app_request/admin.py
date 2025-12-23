from django.contrib import admin
from .models import FZ, ColumnFZ


@admin.register(FZ)
class FZAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)

    verbose_name = 'Закон'
    verbose_name_plural = 'Законы'


@admin.register(ColumnFZ)
class ColumnFZAdmin(admin.ModelAdmin):
    list_display = ('column', 'fz', 'created_at', 'updated_at', 'is_active')
    raw_id_fields = ('column', 'fz',)
    search_fields = ('column__name', 'fz__name')
    list_filter = ('is_active',)
    ordering = ('column', 'fz')

    verbose_name = 'Столбец и Закон'
    verbose_name_plural = 'Столбцы и Законы'
