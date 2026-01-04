from django import forms
from django.contrib import admin
from django.contrib import messages
from django_jsonform.widgets import JSONFormWidget

from .forms import LinkColumnColumnAdminForm
from .models import (
    LinkColumnColumn, DimTypeLink, DimDB, LinkColumn, LinkDB, DimStage,
    DimTableNameType, DimTableType, DimColumnName, LinkTableName,
    LinkSchema, LinkTable, LinkColumnName, TotalData
)
from .utils.syncing_model import sync_database


# === Actions ===
@admin.action(description='Синхронизировать выбранную базу и слой')
def sync_selected(modeladmin, request, queryset):
    total_rows = 0
    errors = []

    for link_db in queryset:
        db_instance = link_db.base
        stage_instance = link_db.stage
        result = sync_database(db_instance, stage_instance)

        if isinstance(result, int):
            total_rows += result
        else:
            errors.append(result)

    if total_rows:
        messages.success(request, f"Синхронизировано {total_rows} строк.")

    if errors:
        for error_msg in errors:
            messages.error(request, error_msg)


# === Forms ===
class LinkColumnForm(forms.ModelForm):
    class Meta:
        model = LinkColumn
        fields = '__all__'
        widgets = {
            'description': JSONFormWidget(
                schema={
                    "type": "object",
                    "title": "Дополнительные параметры",
                    "properties": {
                        "name": {"type": "string", "title": "Название"},
                        "description": {"type": "string", "title": "Описание"},
                        "key": {"type": "string", "title": "Ключ"},
                        "auto": {"type": "string", "title": "Авто"},
                    },
                    "required": [],
                    "additionalProperties": False
                }
            ),
            'default': forms.TextInput(attrs={'size': 20, 'style': 'width: 200px;'}),
        }

    def clean_description(self):
        data = self.cleaned_data.get("description", {})
        return {k: v for k, v in data.items() if v not in ("", None)}


# === Inlines ===
class LinkDBInline(admin.TabularInline):
    model = LinkDB
    extra = 0
    fields = ('version', 'name', 'alias', 'host', 'port', 'stage', 'is_active')
    verbose_name = 'Экземпляр базы'
    verbose_name_plural = 'Экземпляры баз'
    fk_name = 'base'
    autocomplete_fields = ['stage']


class LinkTableNameInline(admin.TabularInline):
    model = LinkTableName
    extra = 0
    fields = ('name', 'type', 'is_publish')
    verbose_name = 'Альтернативное имя'
    verbose_name_plural = 'Альтернативные имена таблиц'
    autocomplete_fields = ['type']


class LinkColumnInline(admin.TabularInline):
    model = LinkColumn
    form = LinkColumnForm
    extra = 0
    fields = ('is_active', 'columns', 'type', 'is_null', 'is_key', 'unique_together', 'description', 'default', 'stage')
    verbose_name = 'Колонка'
    verbose_name_plural = 'Колонки'


# === Admins ===
class BaseAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_filter = ('is_active',)


@admin.register(LinkDB)
class LinkDBAdmin(admin.ModelAdmin):
    search_fields = ('name', 'alias', 'host', 'port')
    list_display = ('name', 'alias', 'host', 'port', 'stage', 'base')
    list_filter = ('is_active', 'stage')
    actions = [sync_selected]
    ordering = ['name']
    autocomplete_fields = ['base', 'stage']


@admin.register(DimTypeLink)
class DimTypeLinkAdmin(BaseAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(DimStage)
class DimStageAdmin(BaseAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(DimTableNameType)
class DimDBTableNameTypeAdmin(BaseAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(DimTableType)
class DimDBTableTypeAdmin(BaseAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name', 'description')
    ordering = ['name']


@admin.register(DimDB)
class DimDBAdmin(BaseAdmin):
    inlines = [LinkDBInline]
    list_display = ('name', 'version', 'is_active')
    search_fields = ('name', 'version', 'description')
    ordering = ['name']


@admin.register(DimColumnName)
class DimColumnNameAdmin(BaseAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(LinkSchema)
class LinkDBSchemaAdmin(BaseAdmin):
    list_display = ('base', 'schema', 'is_active')
    search_fields = ('schema', 'base__name')
    list_filter = BaseAdmin.list_filter + ('base',)
    autocomplete_fields = ['base']
    ordering = ['schema']


@admin.register(LinkTable)
class LinkTableAdmin(BaseAdmin):
    inlines = [LinkTableNameInline, LinkColumnInline]
    list_display = ('name', 'schema', 'type', 'is_active', 'get_alternative_names')
    search_fields = ('name', 'type__name', 'schema__schema', 'description')
    list_filter = BaseAdmin.list_filter + ('type', 'schema')
    autocomplete_fields = ['type', 'schema']
    ordering = ['name']

    def get_alternative_names(self, obj):
        names = obj.linktablename_set.values_list('name', flat=True)
        return ", ".join(names) if names else "—"

    get_alternative_names.short_description = "Альтернативные имена"


@admin.register(LinkColumn)
class LinkColumnAdmin(BaseAdmin):
    form = LinkColumnForm
    list_display = ('columns', 'table', 'type', 'is_null', 'is_key', 'is_active')
    search_fields = [
        'columns',
        'table__name',
        'table__schema__schema',
        'table__schema__base__name'
    ]
    list_filter = BaseAdmin.list_filter + ('type', 'is_null', 'is_key')
    autocomplete_fields = ['table']
    ordering = ['columns']


@admin.register(LinkTableName)
class LinkTableNameAdmin(BaseAdmin):
    list_display = ('table', 'name', 'type', 'is_publish', 'is_active')
    search_fields = ('table__name', 'name', 'type__name')
    autocomplete_fields = ['table', 'type']
    ordering = ['name']


@admin.register(LinkColumnName)
class LinkColumnNameAdmin(BaseAdmin):
    list_display = ('column', 'name', 'is_active')
    search_fields = ('column__columns', 'name__name')
    autocomplete_fields = ['column', 'name']
    ordering = ['name']


@admin.register(TotalData)
class TotalDataAdmin(admin.ModelAdmin):
    list_display = (
        'hash_address', 'table_catalog', 'table_schema', 'table_name',
        'column_name', 'created_at', 'is_active'
    )
    search_fields = ('table_catalog', 'table_schema', 'table_name', 'column_name', 'data_type')
    list_filter = ('is_active', 'stand', 'table_type')
    readonly_fields = ('hash_address', 'created_at', 'updated_at')
    list_per_page = 50
    ordering = ['-created_at']


# === LinkColumnColumn Admin (рабочая версия) ===
@admin.register(LinkColumnColumn)
class LinkColumnColumnAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'main', 'sub', 'is_active']
    list_filter = ['type', 'is_active']
    autocomplete_fields = ['main', 'sub']  # ← Это работает как Google-поиск
    form = LinkColumnColumnAdminForm

    # Не используем autocomplete_fields — конфликтует с кастомной формой
    def main_col_display(self, obj):
        return str(obj.main) if obj.main else "—"

    main_col_display.short_description = "Main"

    def sub_col_display(self, obj):
        return str(obj.sub) if obj.sub else "∅"

    sub_col_display.short_description = "Sub"
