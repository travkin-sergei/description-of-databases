# my_dbm/admin.py
from django import forms
from django.contrib import admin, messages
from django_jsonform.widgets import JSONFormWidget

from .utils.syncing_model import sync_database
from .models import *


# === Формы ===
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
            'default': forms.TextInput(attrs={'size': 20, 'style': 'width: 200px;'}),  # Компактное поле default
        }

    def clean_description(self):
        data = self.cleaned_data.get("description", {})
        return {k: v for k, v in data.items() if v not in ("", None)}


# === Базовый класс админки ===
class BaseAdmin(admin.ModelAdmin):
    """Базовый класс админки с общими настройками"""
    list_per_page = 20
    list_filter = ('is_active',)


# === Справочные модели ===
@admin.register(DimTypeLink)
class DimTypeLinkAdmin(BaseAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)


@admin.register(DimStage)
class DimStageAdmin(BaseAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)


@admin.register(DimDBTableNameType)
class DimDBTableNameTypeAdmin(BaseAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)


@admin.register(DimDBTableType)
class DimDBTableTypeAdmin(BaseAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name', 'description')


@admin.register(DimDB)
class DimDBAdmin(BaseAdmin):
    list_display = ('name', 'version', 'is_active')
    search_fields = ('name', 'version')
    list_filter = BaseAdmin.list_filter


@admin.register(DimColumnName)
class DimColumnNameAdmin(BaseAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)


class LinkDBTableNameInline(admin.TabularInline):
    model = LinkDBTableName
    extra = 0
    fields = ('name', 'type', 'is_publish')
    verbose_name = 'Альтернативное имя'
    verbose_name_plural = 'Альтернативные имена таблиц'


class LinkColumnInline(admin.TabularInline):
    model = LinkColumn
    form = LinkColumnForm  # Используем единую форму
    extra = 0
    fields = ('is_active','columns','type','default','is_null','is_key','unique_together','description','stage',)
    verbose_name = 'Колонка'
    verbose_name_plural = 'Колонки'


# === Основные модели ===
@admin.register(LinkDBSchema)
class LinkDBSchemaAdmin(BaseAdmin):
    list_display = ('base', 'schema', 'is_active')
    search_fields = ('schema', 'base__name')
    list_filter = BaseAdmin.list_filter + ('base',)
    autocomplete_fields = ['base']


@admin.register(LinkDBTable)
class LinkDBTableAdmin(BaseAdmin):
    inlines = [LinkDBTableNameInline, LinkColumnInline]
    list_display = ('name', 'schema', 'type', 'is_active', 'get_alternative_names')
    search_fields = ('name', 'type__name', 'schema__schema')
    list_filter = BaseAdmin.list_filter + ('type', 'schema')
    autocomplete_fields = ['type', 'schema']

    def get_alternative_names(self, obj):
        return ", ".join(obj.linkdbtablename_set.values_list('name', flat=True))

    get_alternative_names.short_description = "Альтернативные имена"


@admin.register(LinkColumn)
class LinkColumnAdmin(BaseAdmin):
    form = LinkColumnForm
    list_display = ('columns', 'table', 'type', 'is_null', 'is_key', 'is_active')
    search_fields = ('columns', 'table__name')
    list_filter = BaseAdmin.list_filter + ('type', 'is_null', 'is_key')
    autocomplete_fields = ['table']


@admin.register(LinkColumnColumn)
class LinkColumnColumnAdmin(BaseAdmin):
    list_display = ('id', 'main', 'sub', 'type', 'is_active')
    search_fields = ('type__name',)
    raw_id_fields = ('main', 'sub',)
    autocomplete_fields = ['type']


@admin.register(LinkDBTableName)
class LinkDBTableNameAdmin(BaseAdmin):
    list_display = ('table', 'name', 'is_active')
    search_fields = ('table__name', 'name')
    raw_id_fields = ('table',)


@admin.action(description='Синхронизировать выбранную базу и слой')
def sync_selected(modeladmin, request, queryset):
    """
    queryset — это выбранные LinkDB записи.
    """

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


@admin.register(LinkDB)
class LinkDBAdmin(admin.ModelAdmin):
    list_display = ('name', 'alias', 'host', 'port', 'stage', 'base')
    actions = [sync_selected]