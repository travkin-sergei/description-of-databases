# app_updates\admin.py
from django.contrib import admin
from .filters import LinkUpdateColAdminForm
from .models import DimUpdateMethod, LinkUpdateCol


@admin.register(LinkUpdateCol)
class LinkUpdateColAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'main', 'sub', 'is_active']
    list_filter = ['type', 'is_active']
    autocomplete_fields = ['main', 'sub']
    form = LinkUpdateColAdminForm

    def main_col_display(self, obj):
        return str(obj.main) if obj.main else "—"

    main_col_display.short_description = "Main"

    def sub_col_display(self, obj):
        return str(obj.sub) if obj.sub else "∅"

    sub_col_display.short_description = "Sub"
