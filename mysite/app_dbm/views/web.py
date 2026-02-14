# app_dbm/views/web.py
from django.db.models import Q, OuterRef, Subquery
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, TemplateView, ListView
from django.views.decorators.csrf import csrf_exempt
from django_filters.views import FilterView

from _common.models import SafePaginator
from app_services.models import LinkServicesTable
from app_updates.models import LinkUpdateCol

from ..models import (
    LinkDB, LinkSchema, LinkTable, LinkColumn,
    LinkColumnColumn, LinkColumnName, LinkTableName, DimTypeLink,
    DimColumnName, DimTableType, DimTableNameType, DimStage, DimDB,
)
from ..filters import (
    LinkDBFilter,
    LinkTableFilter, LinkColumnFilter,
)


# ================== МИКСИНЫ ==================
class PaginationContextMixin:
    """Миксин для добавления контекста пагинации и фильтрации"""

    def get_pagination_context(self, context, filterset=None):
        """Универсальный метод для получения контекста пагинации"""
        # Используем SafePaginator для подсчета
        if hasattr(context.get('paginator'), 'max_limit'):
            max_limit = context['paginator'].max_limit
            if hasattr(context['paginator'], 'real_count'):
                total_count = context['paginator'].real_count
                is_limited = total_count > max_limit
                limited_count = min(total_count, max_limit)
            else:
                total_count = context['paginator'].count
                is_limited = False
                limited_count = total_count
        else:
            total_count = filterset.qs.count() if filterset else 0
            limited_count = total_count
            is_limited = False

        # Количество на текущей странице
        if context.get('page_obj'):
            displayed_count = len(context['page_obj'].object_list)
        else:
            displayed_count = min(total_count, self.paginate_by)

        pagination_context = {
            'total_count': total_count,
            'limited_count': limited_count,
            'is_limited': is_limited,
            'displayed_count': displayed_count,
        }

        # Параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            pagination_context['query_string'] = get_params.urlencode()

        pagination_context['form_submitted'] = bool(self.request.GET)
        pagination_context['has_filter_params'] = any(
            v for k, v in self.request.GET.items() if k != 'page'
        )

        return pagination_context


class AutocompleteMixin:
    """Миксин для автокомплита"""
    paginate_by = 20
    search_fields = []
    display_fields = ['id', 'name']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')

        if q and self.search_fields:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': q})
            queryset = queryset.filter(query)

        return queryset

    def render_to_response(self, context, **response_kwargs):
        """Возвращаем JSON в формате, который ожидает Django admin"""
        results = []
        for obj in context['object_list']:
            result = {'id': obj.id}

            for field in self.display_fields:
                if field != 'id':
                    try:
                        value = getattr(obj, field)
                        result[field] = str(value) if value else ''
                    except AttributeError:
                        result[field] = ''

            result['text'] = self.get_display_text(obj)
            results.append(result)

        return JsonResponse({
            'results': results,
            'pagination': {
                'more': context['page_obj'].has_next() if context.get('page_obj') else False
            }
        }, safe=False)

    def get_display_text(self, obj):
        """Метод для формирования текста отображения (переопределяется)"""
        return str(obj)


# ================== ОБЩИЕ ПРЕДСТАВЛЕНИЯ ==================
class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_dbm/about-app.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


# ================== AJAX ЗАПРОСЫ ==================
class GetSchemasView(View):
    """Получение схем по ID базы данных"""

    def get(self, request):
        db_id = request.GET.get('db_id')
        if not db_id:
            return JsonResponse([], safe=False)
        schemas = LinkSchema.objects.filter(base_id=db_id).values('id', 'schema')
        return JsonResponse(list(schemas), safe=False)


class GetTablesView(View):
    """Получение таблиц по ID схемы"""

    def get(self, request):
        schema_id = request.GET.get('schema_id')
        if not schema_id:
            return JsonResponse([], safe=False)
        tables = LinkTable.objects.filter(schema_id=schema_id).values('id', 'name')
        return JsonResponse(list(tables), safe=False)


class GetColumnsView(View):
    """Получение столбцов по ID таблицы"""

    def get(self, request):
        table_id = request.GET.get('table_id')
        if not table_id:
            return JsonResponse([], safe=False)
        columns = LinkColumn.objects.filter(table_id=table_id).values('id', 'columns')
        return JsonResponse(list(columns), safe=False)


# ================== ОСНОВНЫЕ ПРЕДСТАВЛЕНИЯ ==================
class DatabasesView(LoginRequiredMixin, FilterView, PaginationContextMixin):
    """Список баз данных с фильтрацией."""

    model = LinkDB
    filterset_class = LinkDBFilter
    template_name = 'app_dbm/databases.html'
    context_object_name = 'databases'
    paginate_by = 20
    paginator_class = SafePaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('stage').order_by('alias')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_pagination_context(context, self.filterset))
        return context


class TablesView(LoginRequiredMixin, FilterView, PaginationContextMixin):
    """Список таблиц с фильтрацией."""

    model = LinkTable
    template_name = 'app_dbm/tables.html'
    context_object_name = 'tables'
    paginator_class = SafePaginator
    paginate_by = 20
    filterset_class = LinkTableFilter

    def get_queryset(self):
        alt_name_subquery = LinkTableName.objects.filter(
            table=OuterRef('pk'),
            is_active=True
        ).values('name')[:1]

        queryset = (
            LinkTable.objects
            .select_related('schema', 'schema__base', 'type')
            .annotate(alt_name=Subquery(alt_name_subquery))
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_pagination_context(context, self.filterset))
        return context


class TableDetailView(LoginRequiredMixin, DetailView):
    """Детализация таблицы."""

    model = LinkTable
    template_name = 'app_dbm/tables-detail.html'
    context_object_name = 'tables'

    def get_queryset(self):
        return LinkTable.objects.select_related(
            'schema', 'schema__base', 'type'
        ).prefetch_related('linkcolumn_set')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.object

        columns = table.linkcolumn_set.filter(is_active=True).order_by(
            'unique_together', 'date_create', 'id'
        )

        for col in columns:
            col.stages_from_json = []
            if col.stage and isinstance(col.stage, dict):
                col.stages_from_json = [
                    v for k, v in sorted(col.stage.items(), key=lambda x: int(x[0]))
                ]

        context['columns'] = columns

        context['column_relations'] = (
            LinkColumnColumn.objects
            .filter(Q(main__in=columns) | Q(sub__in=columns))
            .select_related('main', 'sub', 'type')
        )

        services = (
            LinkServicesTable.objects
            .filter(table=table)
            .select_related('service')
        )
        context['services_list'] = services
        context['services_count'] = services.count()

        context['alt_table_names'] = LinkTableName.objects.filter(table=table)
        #  Запрос обновлений данных
        context['update_columns'] = (
            LinkUpdateCol.objects
            .filter(main__in=columns)
            .select_related('type', 'main')
            .order_by('type_id', 'main_id')  # Обязательно для distinct с полями, без этого не работает
            .distinct('type_id', 'main_id')
        )

        return context


class ColumnListView(LoginRequiredMixin, FilterView, PaginationContextMixin):
    """Список столбцов с фильтрацией и пагинацией."""

    model = LinkColumn
    filterset_class = LinkColumnFilter
    template_name = 'app_dbm/columns.html'
    context_object_name = 'columns'
    paginate_by = 20
    paginator_class = SafePaginator

    def get_queryset(self):
        queryset = LinkColumn.objects.filter(is_active=True).select_related(
            'table', 'table__schema', 'table__schema__base', 'table__type',
        ).order_by('table__name', 'columns')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_pagination_context(context, self.filterset))
        return context


class ColumnDetailView(LoginRequiredMixin, DetailView):
    """Детализация столбца."""

    model = LinkColumn
    template_name = 'app_dbm/columns-detail.html'
    context_object_name = 'column'

    def get_queryset(self):
        return (
            LinkColumn.objects
            .filter(is_active=True)
            .select_related('table', 'table__schema', 'table__schema__base', 'table__type')
            .prefetch_related('linkcolumnname_set__name')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column = self.object

        column_relations = LinkColumnColumn.objects.filter(
            Q(main=column) | Q(sub=column)
        ).select_related('main', 'sub', 'type')
        context['column_relations'] = column_relations

        column_names = LinkColumnName.objects.filter(column=column).select_related('name')
        context['column_names'] = column_names

        context['schedules'] = []

        return context


# ================== AJAX ОБРАБОТЧИКИ ==================
@method_decorator(csrf_exempt, name='dispatch')
class LinkColumnColumnCreateView(View):
    """Класс-обработчик для создания связи столбцов через AJAX."""

    def post(self, request, *args, **kwargs):
        try:
            main_id = request.POST.get('main_column')
            sub_id = request.POST.get('sub_column')
            type_id = request.POST.get('type')
            is_active = request.POST.get('is_active') == 'on'

            if not main_id or not type_id:
                return JsonResponse({
                    "error": "Поля 'main_column' и 'type' обязательны"
                }, status=400)

            main_id = int(main_id)
            type_id = int(type_id)
            sub_id = int(sub_id) if sub_id else None

            try:
                main_col = LinkColumn.objects.get(pk=main_id)
                type_obj = DimTypeLink.objects.get(pk=type_id)
                sub_col = LinkColumn.objects.get(pk=sub_id) if sub_id else None
            except LinkColumn.DoesNotExist:
                return JsonResponse({
                    "error": f"Столбец с ID={main_id} не найден"
                }, status=400)
            except DimTypeLink.DoesNotExist:
                return JsonResponse({
                    "error": f"Тип связи с ID={type_id} не найден"
                }, status=400)

            obj = LinkColumnColumn.objects.create(
                main_id=main_id,
                sub_id=sub_id,
                type_id=type_id,
                is_active=is_active
            )

            return JsonResponse({
                "success": True,
                "id": obj.id,
                "main": str(obj.main),
                "sub": str(obj.sub) if obj.sub else None,
                "message": f"✅ Связь #{obj.id} успешно создана"
            })

        except ValueError as e:
            return JsonResponse({
                "error": f"Некорректный числовой идентификатор: {e}"
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "error": str(e),
                "details": "См. логи сервера для деталей"
            }, status=500)


# ================== АВТОКОМПЛИТ ПРЕДСТАВЛЕНИЯ ==================
class LinkColumnAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для столбцов"""
    model = LinkColumn
    search_fields = ['columns', 'table__name', 'table__schema__schema', 'table__schema__base__name']
    display_fields = ['id', 'columns']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'table__schema__base'
        ).order_by('columns')

    def get_display_text(self, obj):
        try:
            return f"{obj.table.schema.base.name}.{obj.table.schema.schema}.{obj.table.name}.{obj.columns}"
        except AttributeError:
            return obj.columns or str(obj)


class LinkTableAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для таблиц"""
    model = LinkTable
    search_fields = ['name', 'schema__schema', 'schema__base__name']
    display_fields = ['id', 'name']

    def get_queryset(self):
        return super().get_queryset().select_related(
            'schema__base'
        ).order_by('name')

    def get_display_text(self, obj):
        try:
            return f"{obj.schema.base.name}.{obj.schema.schema}.{obj.name}"
        except AttributeError:
            return obj.name or str(obj)


class LinkDBAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для баз данных"""
    model = LinkDB
    search_fields = ['name', 'alias', 'stage__name']
    display_fields = ['id', 'name', 'alias']

    def get_queryset(self):
        return super().get_queryset().select_related('stage').order_by('alias')

    def get_display_text(self, obj):
        return f"{obj.alias} ({obj.name})"


class LinkSchemaAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для схем"""
    model = LinkSchema
    search_fields = ['schema', 'base__name']
    display_fields = ['id', 'schema']

    def get_queryset(self):
        return super().get_queryset().select_related('base').order_by('schema')

    def get_display_text(self, obj):
        try:
            return f"{obj.base.name}.{obj.schema}"
        except AttributeError:
            return obj.schema or str(obj)


class DimDBAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для типов баз данных"""
    model = DimDB
    search_fields = ['name', 'version']
    display_fields = ['id', 'name', 'version']

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def get_display_text(self, obj):
        return f"{obj.name} {obj.version}" if obj.version else obj.name


class DimStageAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для стендов"""
    model = DimStage
    search_fields = ['name']
    display_fields = ['id', 'name']

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def get_display_text(self, obj):
        return obj.name


class DimTableNameTypeAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для типов названий таблиц"""
    model = DimTableNameType
    search_fields = ['name']
    display_fields = ['id', 'name']

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def get_display_text(self, obj):
        return obj.name


class DimTableTypeAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для типов таблиц"""
    model = DimTableType
    search_fields = ['name']
    display_fields = ['id', 'name']

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def get_display_text(self, obj):
        return obj.name


class DimColumnNameAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для названий столбцов"""
    model = DimColumnName
    search_fields = ['name']
    display_fields = ['id', 'name']

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def get_display_text(self, obj):
        return obj.name


class DimTypeLinkAutocomplete(ListView, AutocompleteMixin):
    """Автокомплит для типов связей"""
    model = DimTypeLink
    search_fields = ['name']
    display_fields = ['id', 'name']

    def get_queryset(self):
        return super().get_queryset().order_by('name')

    def get_display_text(self, obj):
        return obj.name
