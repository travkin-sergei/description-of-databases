from django.contrib import admin
from django import forms
from django_jsonform.widgets import JSONFormWidget
from .models import *


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


# === Inline классы ===

class LinkColumnStageInline(admin.TabularInline):
    model = LinkColumnStage
    extra = 0
    autocomplete_fields = ['stage']
    verbose_name = 'Этап'
    verbose_name_plural = 'Этапы'
    fields = ('stage', 'is_active')


class LinkDBTableNameInline(admin.TabularInline):
    model = LinkDBTableName
    extra = 1
    fields = ('name', 'is_active')
    verbose_name = 'Альтернативное имя'
    verbose_name_plural = 'Альтернативные имена'


class LinkColumnInline(admin.TabularInline):
    model = LinkColumn
    extra = 0
    fields = ('columns', 'type', 'is_null', 'is_key', 'is_active', 'unique_together')
    verbose_name = 'Колонка'
    verbose_name_plural = 'Колонки'


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
            )
        }

    def clean_description(self):
        data = self.cleaned_data.get("description", {})
        return {k: v for k, v in data.items() if v not in ("", None)}


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
    inlines = [LinkColumnStageInline]
    list_display = ('columns', 'table', 'type', 'is_null', 'is_key', 'is_active')
    search_fields = ('columns', 'table__name')
    list_filter = BaseAdmin.list_filter + ('type', 'is_null', 'is_key')
    autocomplete_fields = ['table']  # Оставляем только table, так как type - это CharField

    fieldsets = (
        (None, {'fields': ('table', 'columns', 'type', 'is_active')}),
        ('Свойства', {'fields': ('is_null', 'is_key', 'default')}),
        ('Описание', {'fields': ('description',)}),
    )


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


@admin.register(LinkDB)
class LinkDBAdmin(BaseAdmin):
    list_display = ('name', 'alias', 'host', 'port', 'stage', 'is_active')
    search_fields = ('name', 'alias', 'host')
    list_filter = BaseAdmin.list_filter + ('stage',)
    autocomplete_fields = ['stage']
