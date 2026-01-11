# app_dbm\views\web.py
import logging

from django.db.models import Q, OuterRef, Subquery
from django.http import HttpResponseNotFound, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.decorators.csrf import csrf_exempt

from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin

from _common.models import SafePaginator
from app_services.models import LinkServicesTable

from ..models import (
    LinkDB, LinkSchema, LinkTable, LinkColumn,
    LinkColumnColumn, LinkColumnName, LinkTableName, DimTypeLink,
)
from ..filters import (
    LinkDBFilter,
    LinkTableFilter, LinkColumnFilter,
)

logger = logging.getLogger(__name__)


class PageNotFoundView(LoginRequiredMixin, View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_dbm/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class DatabasesView(LoginRequiredMixin, FilterView):
    """Список баз данных с фильтрацией."""

    model = LinkDB
    filterset_class = LinkDBFilter
    template_name = 'app_dbm/databases.html'
    context_object_name = 'databases'
    paginate_by = 20
    paginator_class = SafePaginator  # Используем SafePaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('stage').order_by('alias')

        # Применяем фильтры
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        # УБЕРИТЕ СРЕЗ! SafePaginator сам ограничит количество
        # НЕ ДЕЛАЙТЕ: limited_qs = filtered_qs[:self.limit]

        return self.filterset.qs  # Просто возвращаем фильтрованный QuerySet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Используем SafePaginator для подсчета
        if hasattr(context.get('paginator'), 'max_limit'):
            max_limit = context['paginator'].max_limit
            # SafePaginator уже ограничил количество, проверяем через real_count если есть
            if hasattr(context['paginator'], 'real_count'):
                total_count = context['paginator'].real_count
                is_limited = total_count > max_limit
                limited_count = min(total_count, max_limit)
            else:
                total_count = context['paginator'].count
                is_limited = False
                limited_count = total_count
        else:
            # Если не SafePaginator, считаем обычным способом
            total_count = self.filterset.qs.count() if self.filterset else 0
            limited_count = total_count
            is_limited = False

        # Количество на текущей странице
        if context.get('page_obj'):
            displayed_count = len(context['page_obj'].object_list)
        else:
            displayed_count = min(total_count, self.paginate_by)

        context['total_count'] = total_count
        context['limited_count'] = limited_count
        context['is_limited'] = is_limited
        context['displayed_count'] = displayed_count

        # Параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        context['form_submitted'] = bool(self.request.GET)
        context['has_filter_params'] = any(v for k, v in self.request.GET.items() if k != 'page')

        return context


class TablesView(LoginRequiredMixin, FilterView):
    model = LinkTable
    template_name = 'app_dbm/tables.html'
    context_object_name = 'tables'
    paginator_class = SafePaginator  # Используем SafePaginator
    paginate_by = 20
    filterset_class = LinkTableFilter

    def get_queryset(self):
        # Подзапрос для альтернативного имени с is_publish=True
        alt_name_subquery = LinkTableName.objects.filter(
            table=OuterRef('pk'),
            is_active=True
        ).values('name')[:1]

        queryset = (
            LinkTable.objects
            .select_related('schema', 'schema__base', 'type')
            .annotate(alt_name=Subquery(alt_name_subquery))
        )

        # Применяем фильтры
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        # УБЕРИТЕ СРЕЗ! SafePaginator сам ограничит количество
        # НЕ ДЕЛАЙТЕ: limited_qs = filtered_qs[:self.limit]

        return self.filterset.qs  # Просто возвращаем фильтрованный QuerySet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_params = self.request.GET.copy()

        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        context['form_submitted'] = bool(self.request.GET)
        context['has_filter_params'] = any(v for k, v in self.request.GET.items() if k != 'page')

        # Используем SafePaginator для подсчета
        if hasattr(context.get('paginator'), 'max_limit'):
            max_limit = context['paginator'].max_limit
            # SafePaginator уже ограничил количество, проверяем через real_count если есть
            if hasattr(context['paginator'], 'real_count'):
                total_count = context['paginator'].real_count
                is_limited = total_count > max_limit
                limited_count = min(total_count, max_limit)
            else:
                total_count = context['paginator'].count
                is_limited = False
                limited_count = total_count
        else:
            # Если не SafePaginator, считаем обычным способом
            total_count = self.filterset.qs.count() if self.filterset else 0
            limited_count = total_count
            is_limited = False

        # Количество отображаемых записей (с учетом пагинации)
        if context.get('page_obj'):
            displayed_count = len(context['page_obj'].object_list)
        else:
            displayed_count = min(total_count, self.paginate_by)

        context['total_count'] = total_count
        context['limited_count'] = limited_count
        context['is_limited'] = is_limited
        context['displayed_count'] = displayed_count

        return context


class TableDetailView(LoginRequiredMixin, DetailView):
    """Детализация таблицы."""

    model = LinkTable
    template_name = 'app_dbm/tables-detail.html'
    context_object_name = 'tables'

    def get_queryset(self):
        return LinkTable.objects.select_related(
            'schema', 'schema__base', 'type'
        ).prefetch_related(
            'linkcolumn_set'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.object

        # Существующие столбцы
        columns = table.linkcolumn_set.filter(is_active=True).order_by(
            'unique_together', 'date_create', 'id'
        )

        # Добавляем stage из JSON
        for col in columns:
            col.stages_from_json = []
            if col.stage and isinstance(col.stage, dict):
                # Сортируем по ключу и сохраняем список стадий
                col.stages_from_json = [
                    v for k, v in sorted(col.stage.items(), key=lambda x: int(x[0]))
                ]

        context['columns'] = columns

        # Связи между столбцами
        context['column_relations'] = LinkColumnColumn.objects.filter(
            Q(main__in=columns) | Q(sub__in=columns)
        ).select_related('main', 'sub', 'type')

        # Связанные сервисы
        services = LinkServicesTable.objects.filter(table=table).select_related('service')
        context['services_list'] = services
        context['services_count'] = services.count()

        # Расписания обновлений
        schedules = LinkUpdate.objects.filter(
            is_active=True,
            column__main__table=table,
        ).values(
            'name__id',
            'name__name',
            'name__schedule',
            'name__is_active'
        ).distinct().order_by('name__name')
        context['schedules'] = schedules

        # Альтернативные имена таблицы
        alt_names = LinkTableName.objects.filter(table=table)
        context['alt_table_names'] = alt_names

        return context


class ColumnListView(LoginRequiredMixin, FilterView):
    """Список столбцов с фильтрацией и пагинацией."""

    model = LinkColumn
    filterset_class = LinkColumnFilter
    template_name = 'app_dbm/columns.html'
    context_object_name = 'columns'
    paginate_by = 20
    paginator_class = SafePaginator  # Используем SafePaginator

    def get_queryset(self):
        # Получаем базовый queryset
        queryset = LinkColumn.objects.filter(is_active=True).select_related(
            'table',
            'table__schema',
            'table__schema__base',
            'table__type',
        ).order_by('table__name', 'columns')

        # Применяем фильтры
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        # УБЕРИТЕ СРЕЗ! SafePaginator сам ограничит количество
        # НЕ ДЕЛАЙТЕ: limited_qs = filtered_qs[:self.limit]

        return self.filterset.qs  # Просто возвращаем фильтрованный QuerySet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Используем SafePaginator для подсчета
        if hasattr(context.get('paginator'), 'max_limit'):
            max_limit = context['paginator'].max_limit
            # SafePaginator уже ограничил количество, проверяем через real_count если есть
            if hasattr(context['paginator'], 'real_count'):
                total_count = context['paginator'].real_count
                is_limited = total_count > max_limit
                limited_count = min(total_count, max_limit)
            else:
                total_count = context['paginator'].count
                is_limited = False
                limited_count = total_count
        else:
            # Если не SafePaginator, считаем обычным способом
            total_count = self.filterset.qs.count() if self.filterset else 0
            limited_count = total_count
            is_limited = False

        # Количество на текущей странице
        if context.get('page_obj'):
            displayed_count = len(context['page_obj'].object_list)
        else:
            displayed_count = min(total_count, self.paginate_by)

        context['total_count'] = total_count
        context['limited_count'] = limited_count
        context['is_limited'] = is_limited
        context['displayed_count'] = displayed_count

        # Для пагинации с сохранением параметров фильтрации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        if get_params:
            context['query_string'] = get_params.urlencode()

        # Добавляем флаги для отображения правильного интерфейса
        context['form_submitted'] = bool(self.request.GET)
        context['has_filter_params'] = any(v for k, v in self.request.GET.items() if k != 'page')

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
            .select_related(
                'table',
                'table__schema',
                'table__schema__base',
                'table__type'
            ).prefetch_related(
                'linkcolumnname_set__name',
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column = self.object

        # Получить связи столбца (главный или подчинённый)
        column_relations = LinkColumnColumn.objects.filter(
            Q(main=column) | Q(sub=column)
        ).select_related('main', 'sub', 'type')
        context['column_relations'] = column_relations

        # Синонимы названий столбцов
        column_names = LinkColumnName.objects.filter(column=column).select_related('name')
        context['column_names'] = column_names

        # Обновления
        schedules = LinkUpdate.objects.filter(
            column__main=column
        ).values(
            'name__id',
            'name__name',
            'name__schedule',
            'name__is_active'
        ).distinct().order_by('name__name')
        context['schedules'] = schedules

        return context


class SchemaAPIView(View):
    def get(self, request):
        dim_db_id = request.GET.get('dim_db')
        schemas = LinkSchema.objects.filter(base_id=dim_db_id).values('id', 'schema')
        return JsonResponse(list(schemas), safe=False)


class TableAPIView(View):
    def get(self, request):
        schema_id = request.GET.get('schema')
        tables = LinkTable.objects.filter(schema_id=schema_id).values('id', 'name')
        return JsonResponse(list(tables), safe=False)


class ColumnAPIView(View):
    def get(self, request):
        table_id = request.GET.get('table')
        columns = LinkColumn.objects.filter(table_id=table_id).values('id', 'columns')
        return JsonResponse(list(columns), safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class LinkColumnColumnCreateView(View):
    """
    Класс-обработчик для создания связи столбцов через AJAX.
    Используется в админке, когда стандартное сохранение ломается.
    """

    def post(self, request, *args, **kwargs):
        try:
            # Извлекаем данные
            main_id = request.POST.get('main_column')
            sub_id = request.POST.get('sub_column')
            type_id = request.POST.get('type')
            is_active = request.POST.get('is_active') == 'on'

            # Валидация
            if not main_id or not type_id:
                return JsonResponse({
                    "error": "Поля 'main_column' и 'type' обязательны"
                }, status=400)

            # Преобразуем в int
            main_id = int(main_id)
            type_id = int(type_id)
            sub_id = int(sub_id) if sub_id else None

            # Проверяем существование объектов (защита от 500)
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

            # Создаём запись напрямую — минуя админку и формы
            obj = LinkColumnColumn.objects.create(
                main_id=main_id,
                sub_id=sub_id,
                type_id=type_id,
                is_active=is_active
            )

            logger.info(f"LinkColumnColumn #{obj.id} создан: main={main_id}, sub={sub_id}, type={type_id}")

            return JsonResponse({
                "success": True,
                "id": obj.id,
                "main": str(obj.main),
                "sub": str(obj.sub) if obj.sub else None,
                "message": f"✅ Связь #{obj.id} успешно создана"
            })

        except ValueError as e:
            logger.error(f"Некорректный ID: {e}")
            return JsonResponse({
                "error": f"Некорректный числовой идентификатор: {e}"
            }, status=400)

        except Exception as e:
            logger.exception("Ошибка при создании LinkColumnColumn")
            return JsonResponse({
                "error": str(e),
                "details": "См. логи сервера для деталей"
            }, status=500)
