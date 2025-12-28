# app_dbm/admin.py
from django import forms
from django.contrib import admin, messages
from django_jsonform.widgets import JSONFormWidget

from .utils.syncing_model import sync_database
from .models import *


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


# Inline для LinkDB в админке DimDB
class LinkDBInline(admin.TabularInline):
    """Инлайн для показа связанных LinkDB в DimDB"""
    model = LinkDB
    extra = 0
    fields = ('version', 'name', 'alias', 'host', 'port', 'stage', 'is_active')
    verbose_name = 'Экземпляр базы'
    verbose_name_plural = 'Экземпляры баз'
    fk_name = 'base'  # Указываем поле ForeignKey
    # Добавляем автокомплит для ForeignKey в inline
    autocomplete_fields = ['stage']


# 03 Список баз данных.
@admin.register(LinkDB)
class LinkDBAdmin(admin.ModelAdmin):
    search_fields = ('name', 'alias', 'host', 'port')
    list_display = ('name', 'alias', 'host', 'port', 'stage', 'base')
    list_filter = ('is_active', 'stage')
    actions = [sync_selected]
    ordering = ['name']
    # Добавляем автокомплит для ForeignKey полей
    autocomplete_fields = ['base', 'stage']


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
    ordering = ['name']


@admin.register(DimStage)
class DimStageAdmin(BaseAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(DimDBTableNameType)
class DimDBTableNameTypeAdmin(BaseAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


@admin.register(DimDBTableType)
class DimDBTableTypeAdmin(BaseAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name', 'description')
    ordering = ['name']


@admin.register(DimDB)
class DimDBAdmin(BaseAdmin):
    inlines = [LinkDBInline]
    list_display = ('name', 'version', 'is_active')
    search_fields = ('name', 'version', 'description')
    list_filter = BaseAdmin.list_filter
    ordering = ['name']


# 08 Словарь имен столбцов.
@admin.register(DimColumnName)
class DimColumnNameAdmin(BaseAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    ordering = ['name']


class LinkDBTableNameInline(admin.TabularInline):
    model = LinkDBTableName
    extra = 0
    fields = ('name', 'type', 'is_publish')
    verbose_name = 'Альтернативное имя'
    verbose_name_plural = 'Альтернативные имена таблиц'
    # Добавляем автокомплит для ForeignKey в inline
    autocomplete_fields = ['type']


class LinkColumnInline(admin.TabularInline):
    model = LinkColumn
    form = LinkColumnForm  # Используем единую форму
    extra = 0
    fields = ('is_active', 'columns', 'type', 'is_null', 'is_key', 'unique_together', 'description', 'default',
              'stage',)
    verbose_name = 'Колонка'
    verbose_name_plural = 'Колонки'


# 04 Схемы баз данных.
@admin.register(LinkDBSchema)
class LinkDBSchemaAdmin(BaseAdmin):
    list_display = ('base', 'schema', 'is_active')
    search_fields = ('schema', 'base__name')
    list_filter = BaseAdmin.list_filter + ('base',)
    autocomplete_fields = ['base']
    ordering = ['schema']


# 10 Таблица.
@admin.register(LinkDBTable)
class LinkDBTableAdmin(BaseAdmin):
    inlines = [LinkDBTableNameInline, LinkColumnInline]
    list_display = ('name', 'schema', 'type', 'is_active', 'get_alternative_names')
    search_fields = ('name', 'type__name', 'schema__schema', 'description')
    list_filter = BaseAdmin.list_filter + ('type', 'schema')
    autocomplete_fields = ['type', 'schema']
    ordering = ['name']

    def get_alternative_names(self, obj):
        names = obj.linkdbtablename_set.values_list('name', flat=True)
        return ", ".join(names) if names else "—"

    get_alternative_names.short_description = "Альтернативные имена"


@admin.register(LinkColumn)
class LinkColumnAdmin(BaseAdmin):
    form = LinkColumnForm
    list_display = ('columns', 'table', 'type', 'is_null', 'is_key', 'is_active')
    search_fields = ('columns', 'table__name', 'type', 'description')
    list_filter = BaseAdmin.list_filter + ('type', 'is_null', 'is_key')
    autocomplete_fields = ['table']
    ordering = ['columns']


@admin.register(LinkColumnColumn)
class LinkColumnColumnAdmin(BaseAdmin):
    list_display = ('id', 'main', 'sub', 'type', 'is_active')
    search_fields = ('type__name', 'main__columns', 'sub__columns')
    autocomplete_fields = ['main', 'sub', 'type']
    ordering = ['main']


@admin.register(LinkDBTableName)
class LinkDBTableNameAdmin(BaseAdmin):
    list_display = ('table', 'name', 'type', 'is_publish', 'is_active')
    search_fields = ('table__name', 'name', 'type__name')
    autocomplete_fields = ['table', 'type']
    ordering = ['name']


# Добавляем админку для LinkColumnName, если она используется
@admin.register(LinkColumnName)
class LinkColumnNameAdmin(BaseAdmin):
    list_display = ('column', 'name', 'is_active')
    search_fields = ('column__columns', 'name__name')
    autocomplete_fields = ['column', 'name']
    ordering = ['name']


# Регистрируем TotalData с автокомплитом
@admin.register(TotalData)
class TotalDataAdmin(admin.ModelAdmin):
    list_display = (
        'hash_address', 'table_catalog', 'table_schema', 'table_name', 'column_name', 'created_at', 'is_active')
    search_fields = ('table_catalog', 'table_schema', 'table_name', 'column_name', 'data_type')
    list_filter = ('is_active', 'stand', 'table_type')
    readonly_fields = ('hash_address', 'created_at', 'updated_at')
    list_per_page = 50
    ordering = ['-created_at']
