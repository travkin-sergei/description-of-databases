# admin.py
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
            )
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
    form = LinkColumnForm  # Добавляем твою форму здесь!
    extra = 0
    fields = ('is_active', 'columns', 'type', 'is_null', 'is_key', 'description', 'unique_together')
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


# @admin.register(LinkDB)
# class LinkDBAdmin(BaseAdmin):
#     list_display = ('name', 'alias', 'host', 'port', 'stage', 'is_active')
#     search_fields = ('name', 'alias', 'host')
#     list_filter = BaseAdmin.list_filter + ('stage',)
#     autocomplete_fields = ['stage']


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

# @admin.register(LinkDB)
# class LinkDBAdmin(admin.ModelAdmin):
#     list_display = ("stage", "get_data_base", "is_active")
#     search_fields = ("stage__name", "data_base__name")
#     actions = ["sync_selected_databases"]
#
#     @admin.display(description='Database')
#     def get_data_base(self, obj):
#         return obj.base.name
#
#     def sync_selected_databases(self, request, queryset):
#         processed = 0
#
#         try:
#             with transaction.atomic():
#                 for linkdb in queryset:
#                     stage_name = (linkdb.stage.name or "").strip()
#                     db_name = (linkdb.base.name or "").strip()
#
#                     if not stage_name or not db_name:
#                         continue
#
#                     total_qs = TotalData.objects.filter(
#                         stage=stage_name,
#                         db_name=db_name,
#                         is_active=True
#                     )
#
#                     created = {
#                         "stages": set(),
#                         "dbs": set(),
#                         "schemas": set(),
#                         "table_types": set(),
#                         "tables": set(),
#                         "columns": set(),
#                         "col_stages": set(),
#                     }
#
#                     for td in total_qs:
#                         # --- DimStage ---
#                         stage_obj, _ = DimStage.objects.get_or_create(name=stage_name)
#                         stage_obj.description = td.schem_description or stage_obj.description
#                         stage_obj.is_active = True
#                         stage_obj.save()
#                         created["stages"].add(stage_obj.pk)
#
#                         # --- DimDB ---
#                         db_obj, _ = DimDB.objects.get_or_create(name=db_name)
#                         db_obj.version = td.db_version or db_obj.version
#                         db_obj.description = td.db_description or db_obj.description
#                         db_obj.is_active = True
#                         db_obj.save()
#                         created["dbs"].add(db_obj.pk)
#
#                         # --- LinkDBSchema ---
#                         schema_name = (td.schem_name or "").strip()
#                         schema_obj = None
#                         if schema_name:
#                             schema_obj, _ = LinkDBSchema.objects.get_or_create(base=db_obj, schema=schema_name)
#                             schema_obj.description = td.schem_description or schema_obj.description
#                             schema_obj.is_active = True
#                             schema_obj.save()
#                             created["schemas"].add((schema_obj.base_id, schema_obj.schema))
#
#                         # --- DimDBTableType ---
#                         tab_type = (td.tab_type or "").strip()
#                         tab_type_obj = None
#                         if tab_type:
#                             tab_type_obj, _ = DimDBTableType.objects.get_or_create(name=tab_type)
#                             tab_type_obj.description = td.tab_description or tab_type_obj.description
#                             tab_type_obj.is_active = True
#                             tab_type_obj.save()
#                             created["table_types"].add(tab_type_obj.pk)
#
#                         # --- LinkDBTable ---
#                         tab_name = (td.tab_name or "").strip()
#                         table_obj = None
#                         if schema_obj and tab_type_obj and tab_name:
#                             table_obj, _ = LinkDBTable.objects.get_or_create(
#                                 schema=schema_obj, type=tab_type_obj, name=tab_name
#                             )
#                             table_obj.is_metadata = bool(td.tab_is_metadata)
#                             table_obj.description = td.tab_description or table_obj.description
#                             table_obj.is_active = True
#                             table_obj.save()
#                             created["tables"].add((table_obj.schema_id, table_obj.type_id, table_obj.name))
#
#                         # --- LinkColumn ---
#                         col_cols = (td.col_columns or "").strip()
#                         col_obj = None
#                         if table_obj and col_cols:
#                             col_obj, _ = LinkColumn.objects.get_or_create(table=table_obj, columns=col_cols)
#                             if td.col_type:
#                                 col_obj.type = td.col_type
#                             if td.col_date_create:
#                                 col_obj.date_create = td.col_date_create
#                             col_obj.is_null = bool(td.col_is_null) if td.col_is_null is not None else col_obj.is_null
#                             col_obj.is_key = bool(td.col_is_key) if td.col_is_key is not None else col_obj.is_key
#                             col_obj.unique_together = td.col_unique_together
#                             col_obj.default = td.col_default or col_obj.default
#                             col_obj.description = td.col_description or col_obj.description
#                             col_obj.is_active = True
#                             col_obj.save()
#                             created["columns"].add((col_obj.table_id, col_obj.columns))
#
#                         # --- LinkColumnStage ---
#                         if stage_obj and col_obj:
#                             cs_obj, _ = LinkColumnStage.objects.get_or_create(stage=stage_obj, column=col_obj)
#                             cs_obj.is_active = True
#                             cs_obj.save()
#                             created["col_stages"].add((cs_obj.stage_id, cs_obj.column_id))
#
#                     # ===== Деактивация только в рамках выбранного stage/db =====
#                     if created["stages"]:
#                         DimStage.objects.filter(name=stage_name).exclude(pk__in=created["stages"]).update(
#                             is_active=False)
#                     else:
#                         DimStage.objects.filter(name=stage_name).update(is_active=False)
#
#                     if created["dbs"]:
#                         DimDB.objects.filter(name=db_name).exclude(pk__in=created["dbs"]).update(is_active=False)
#                     else:
#                         DimDB.objects.filter(name=db_name).update(is_active=False)
#
#                     if created["schemas"]:
#                         filters = [models.Q(base_id=b, schema=s) for (b, s) in created["schemas"]]
#                         combined_filter = reduce(or_, filters)
#                         LinkDBSchema.objects.filter(base__name=db_name).exclude(combined_filter).update(is_active=False)
#                     else:
#                         LinkDBSchema.objects.filter(base__name=db_name).update(is_active=False)
#
#                     if created["table_types"]:
#                         DimDBTableType.objects.exclude(pk__in=created["table_types"]).update(is_active=False)
#                     else:
#                         DimDBTableType.objects.update(is_active=False)
#
#                     if created["tables"]:
#                         filters = [models.Q(schema_id=sid, type_id=tid, name=name) for (sid, tid, name) in
#                                    created["tables"]]
#                         combined_filter = reduce(or_, filters)
#                         LinkDBTable.objects.filter(schema__base__name=db_name).exclude(combined_filter).update(
#                             is_active=False)
#                     else:
#                         LinkDBTable.objects.filter(schema__base__name=db_name).update(is_active=False)
#
#                     if created["columns"]:
#                         filters = [models.Q(table_id=t, columns=cols) for (t, cols) in created["columns"]]
#                         combined_filter = reduce(or_, filters)
#                         LinkColumn.objects.filter(table__schema__base__name=db_name).exclude(combined_filter).update(
#                             is_active=False)
#                     else:
#                         LinkColumn.objects.filter(table__schema__base__name=db_name).update(is_active=False)
#
#                     if created["col_stages"]:
#                         filters = [models.Q(stage_id=s, column_id=c) for (s, c) in created["col_stages"]]
#                         combined_filter = reduce(or_, filters)
#                         LinkColumnStage.objects.filter(stage__name=stage_name).exclude(combined_filter).update(
#                             is_active=False)
#                     else:
#                         LinkColumnStage.objects.filter(stage__name=stage_name).update(is_active=False)
#
#                     processed += total_qs.count()
#
#             self.message_user(request, f"Синхронизация завершена. Обработано {processed} строк.")
#         except Exception as e:
#             self.message_user(request, f"Ошибка синхронизации: {e}", level=messages.ERROR)
