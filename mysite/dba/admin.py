from django.contrib import admin
from django.db.models import Q, Value, CharField, Case, When, IntegerField, F
from django.db.models.functions import Concat
from django.db.models import Func
from hashlib import sha256

from .models import (
    Base,
    BaseGroup,
    Schema,
    Table,
    Column,
    StageType,
    Function,
    Service,
    ServiceTable,
)


class ColumnInline(admin.TabularInline):
    model = Column
    extra = 0


class HashAddressMixin:
    def get_hash_address(self, *args):
        data = ''.join(str(a) for a in args)
        return sha256(data.encode()).hexdigest()

    def save_model(self, request, obj, form, change):
        obj.hash_address = self.get_hash_address(*self.hash_args(obj))
        super().save_model(request, obj, form, change)


def annotate_search(qs, field_name, term):
    """
    Аннотирует queryset двумя полями:
      - priority: 0 если startswith, 1 если contains, 2 иначе
      - pos: позиция первого вхождения term в field_name (или большое число)
    """
    # SQL-функция для позиции: Postgres STRPOS, MySQL INSTR, SQLite INSTR
    # Подбор function в зависимости от backend, здесь — PostgreSQL STRPOS:
    pos_func = Func(F(field_name), Value(term), function='STRPOS', output_field=IntegerField())

    return qs.annotate(
        priority=Case(
            When(**{f"{field_name}__istartswith": term}, then=0),
            When(**{f"{field_name}__icontains": term}, then=1),
            default=2,
            output_field=IntegerField(),
        ),
        pos=pos_func
    ).filter(**{f"{field_name}__icontains": term})


def get_ordered(qs, field_name):
    # Сортируем по priority, затем по pos (левее выше), затем по самому полю
    return qs.order_by('priority', 'pos', field_name)


@admin.register(BaseGroup)
class BaseGroupAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('table_catalog', 'hash_address')
    search_fields = ('table_catalog',)
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.table_catalog]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        qs = annotate_search(queryset, 'table_catalog', term)
        return get_ordered(qs, 'table_catalog'), False


@admin.register(StageType)
class StageTypeAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('name', 'hash_address')
    search_fields = ('name',)
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.name]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        qs = annotate_search(queryset, 'name', term)
        return get_ordered(qs, 'name'), False


@admin.register(Service)
class ServiceAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('service', 'hash_address')
    search_fields = ('service',)
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.service]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        qs = annotate_search(queryset, 'service', term)
        return get_ordered(qs, 'service'), False


@admin.register(Base)
class BaseAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('host_db', 'base', 'type', 'version', 'hash_address')
    search_fields = ('host_db', 'base__table_catalog', 'type__name')
    autocomplete_fields = ['base', 'type']
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.host_db, obj.base_id, obj.type_id, obj.version]


@admin.register(Schema)
class SchemaAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('table_schema', 'base', 'hash_address')
    search_fields = ('table_schema', 'base__table_catalog')
    autocomplete_fields = ['base']
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.table_schema, obj.base_id]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        qs = annotate_search(queryset, 'table_schema', term)
        return get_ordered(qs, 'table_schema'), False


@admin.register(Table)
class TableAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('table_name', 'schema', 'type', 'is_metadata', 'hash_address')
    search_fields = ('table_name', 'schema__table_schema', 'schema__base__table_catalog')
    inlines = [ColumnInline]
    autocomplete_fields = ['schema']
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.table_name, obj.schema_id, obj.type, obj.is_metadata]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        qs = annotate_search(queryset, 'table_name', term)
        return get_ordered(qs, 'table_name'), False


@admin.register(Function)
class FunctionAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('name_fun', 'schema', 'hash_address')
    search_fields = ('name_fun', 'schema__table_schema')
    autocomplete_fields = ['schema']
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.name_fun, obj.schema_id]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        qs = annotate_search(queryset, 'name_fun', term)
        return get_ordered(qs, 'name_fun'), False


@admin.register(ServiceTable)
class ServiceTableAdmin(HashAddressMixin, admin.ModelAdmin):
    list_display = ('service', 'table', 'hash_address')
    search_fields = ('service__service', 'table__table_name')
    autocomplete_fields = ['service', 'table']
    readonly_fields = ('hash_address',)

    def hash_args(self, obj):
        return [obj.service_id, obj.table_id]

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if not term:
            return queryset, False
        # для ServiceTable придётся аннотировать оба поля и выбирать один
        qs = annotate_search(
            annotate_search(queryset, 'service__service', term),
            'table__table_name',
            term
        )
        # сортируем по priority/service__service first, затем по table__table_name
        return qs.order_by('priority', 'pos', 'service__service', 'table__table_name'), False
