from django.contrib import admin
from django.db.models import Q, Case, When, IntegerField, Value
from django.db.models.functions import Concat
from .models import *


def make_search_ordering(queryset, search_term, *fields):
    """
    Создает условия для поиска и упорядочивания результатов.
    Ищет все слова по порядку слева направо.
    """
    search_words = search_term.split()

    # Создаем условия для фильтрации
    q_objects = Q()
    for word in search_words:
        word_q = Q()
        for field in fields:
            word_q |= Q(**{f"{field}__icontains": word})
        q_objects &= word_q

    # Создаем условия для упорядочивания
    whens = []
    for i, field in enumerate(fields):
        # Полное совпадение поля
        whens.append(When(**{field: search_term}, then=Value(i * 10)))
        # Начинается с поискового запроса
        whens.append(When(**{f"{field}__istartswith": search_term}, then=Value(i * 10 + 1)))
        # Содержит все слова по порядку
        concat_pattern = " ".join([f"%{word}%" for word in search_words])
        whens.append(When(**{f"{field}__iregex": r'\y' + r'\y.*\y'.join(search_words) + r'\y'},
                          then=Value(i * 10 + 2)))

    # Добавляем условия для каждого слова по отдельности
    for i, field in enumerate(fields):
        for word in search_words:
            whens.append(When(**{f"{field}__istartswith": word}, then=Value(100 + i * 10 + 1)))
            whens.append(When(**{f"{field}__icontains": word}, then=Value(100 + i * 10 + 2)))

    return queryset.filter(q_objects).order_by(
        Case(
            *whens,
            default=1000,
            output_field=IntegerField(),
        ),
        *fields
    )


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('code', 'name')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'code', 'name')
        return queryset, use_distinct


@admin.register(BaseGroup)
class BaseGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_catalog', 'is_active', 'created_at', 'updated_at')
    search_fields = ('table_catalog',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'table_catalog')
        return queryset, use_distinct


@admin.register(StageType)
class StageTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'name')
        return queryset, use_distinct


@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'base', 'type', 'host_db', 'host_name', 'version', 'is_active')
    list_filter = ('type', 'base')
    search_fields = ('host_db', 'base')

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'host_db', 'base')
        return queryset, use_distinct


@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'base', 'table_schema', 'comment', 'is_active')
    search_fields = ('table_schema', 'comment')
    autocomplete_fields = ['base']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'table_schema', 'comment')
        return queryset, use_distinct


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'table_name', 'schema', 'type', 'is_metadata', 'is_active')
    list_filter = ('type', 'is_metadata', 'schema')
    search_fields = ('table_name', 'table_com')
    filter_horizontal = ('tablenames',)
    autocomplete_fields = ['schema', 'tablenames']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'table_name', 'table_com')
        return queryset, use_distinct


@admin.register(TableName)
class TableNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'table', 'language', 'is_active')
    search_fields = ('name',)
    autocomplete_fields = ['table', 'language']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'name')
        return queryset, use_distinct


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'column_name', 'data_type', 'is_nullable', 'is_auto', 'is_active')
    search_fields = ('column_name',)
    list_filter = ('data_type',)
    autocomplete_fields = ['table']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'column_name')
        return queryset, use_distinct


@admin.register(ColumnMDType)
class ColumnMDTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'md_type', 'is_active')
    search_fields = ('md_type',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'md_type')
        return queryset, use_distinct


@admin.register(StageColumn)
class StageColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage', 'column', 'is_active')
    search_fields = ('stage__host_db', 'column__column_name')
    autocomplete_fields = ['stage', 'column']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'stage__host_db', 'column__column_name')
        return queryset, use_distinct


@admin.register(ColumnColumn)
class ColumnColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'main', 'sub', 'type', 'update', 'is_active')
    list_filter = ('type',)
    autocomplete_fields = ['main', 'sub', 'update']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'main__column_name', 'sub__column_name')
        return queryset, use_distinct


@admin.register(UpdateMethod)
class UpdateMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', 'is_active')
    search_fields = ('method',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'method')
        return queryset, use_distinct


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'schedule', 'method', 'is_active')
    search_fields = ('name', 'type')
    list_filter = ('type',)
    autocomplete_fields = ['method']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'name', 'type')
        return queryset, use_distinct


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'name_fun', 'is_active')
    search_fields = ('name_fun',)
    autocomplete_fields = ['schema']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'name_fun')
        return queryset, use_distinct


@admin.register(StageFunction)
class StageFunctionAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage', 'function', 'is_active')
    autocomplete_fields = ['stage', 'function']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'stage__host_db', 'function__name_fun')
        return queryset, use_distinct


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'is_active')
    search_fields = ('service',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'service')
        return queryset, use_distinct


@admin.register(ServiceTable)
class ServiceTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'table', 'is_active')
    search_fields = ('service__service', 'table__table_name')
    autocomplete_fields = ['service', 'table']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = make_search_ordering(queryset, search_term, 'service__service', 'table__table_name')
        return queryset, use_distinct