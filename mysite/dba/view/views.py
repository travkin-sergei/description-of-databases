from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponse, HttpRequest
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Prefetch
from ..filters import *
from ..my_function.cron import get_cron


def page_note_found(request, exception):
    # обработка 404 ошибки отсутствия страницы
    HttpResponseNotFound("<h1>Страница не найдено 404 ошибка</h1>")


def about_me(request):
    """
    Отображение информации о текущем приложении из шалона.
    """

    return render(request, 'dba/about_application.html')


class FilteredListView(ListView):
    """
    Класс фильтрации данных.
    Необходим для сокращения кода объектов класса ListView т.к. имеется пагинация
    """

    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        self.filter = self.filter_class(self.request.GET, queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context


class BasesView(LoginRequiredMixin, FilteredListView):
    """
    Отображение списка баз данных
    """

    permission_required = "dba.view_basegroup"
    template_name = 'dba/bases.html'
    model = BaseGroup
    filter_class = BaseGroupFilter


class BasesViewId(LoginRequiredMixin, DetailView):
    """Отображение описание базы данных"""

    model = BaseGroup
    template_name = 'dba/bases-detail.html'
    context_object_name = 'base_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'view_news'
        context['base'] = Base.objects.filter(base_id=self.object.pk)
        context['user_in_group'] = self.request.user.groups.filter(name='view_basegroup').exists()
        return context


class FunctionView(LoginRequiredMixin, View):
    """
    Отображение списка баз функций
    !!!Рассмотреть возможность удаления данного блока
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        filter = FunctionFilter(request.GET, queryset=Function.objects.all())

        # пагинатор
        paginator_filter = Paginator(filter.qs, 20)
        page_number = request.GET.get('page')
        person_page_odj = paginator_filter.get_page(page_number)
        context = {
            'title': 'defFunctionView',
            'person_page_odj': person_page_odj,
            'filter': filter
        }
        return render(request, 'dba/functions.html', context=context)


class FunctionViewId(LoginRequiredMixin, DetailView):
    """
    Отображение  функции базы данных
    """

    template_name = 'dba/functions-detail.html'
    model = Function
    context_object_name = 'function'

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        function = Function.objects.get(pk=pk)
        stage = StageFunction.objects.filter(function_id=pk).filter(is_active=True)
        context = {
            'title': 'defFunctionView_id',
            'function': function,
            'stage': stage,
        }
        return render(request, 'dba/functions-detail.html', context=context)


class TableView(LoginRequiredMixin, FilteredListView):
    template_name = 'dba/tables.html'
    model = Table
    filter_class = TableFilter
    context_object_name = 'tables'  # Явно задаем имя переменной в контексте

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True, is_metadata=False)

        table_catalog_query = self.request.GET.get('table_catalog', '')
        schema_query = self.request.GET.get('schema', '')
        table_name_query = self.request.GET.get('table_name', '')
        is_active_query = self.request.GET.get('is_active', '')

        if table_catalog_query:
            queryset = queryset.filter(schema__base__table_catalog__icontains=table_catalog_query)
        if schema_query:
            queryset = queryset.filter(schema__table_schema__icontains=schema_query)
        if table_name_query:
            queryset = queryset.filter(
                Q(table_name__icontains=table_name_query) |
                Q(names__name__icontains=table_name_query)
            ).distinct()
        if is_active_query:
            queryset = queryset.filter(is_active=is_active_query == 'true')

        # Оптимизация запросов - prefetch_related для связанных имен с языком
        queryset = queryset.select_related('schema__base').prefetch_related(
            Prefetch('names', queryset=TableName.objects.select_related('language')))

        self.filter = self.filter_class(self.request.GET, queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Собираем все языки для фильтрации
        languages = Language.objects.all()
        context['languages'] = languages

        # Получаем выбранный язык из GET-параметров или используем первый доступный
        selected_lang = self.request.GET.get('lang', languages.first().code if languages.exists() else '')
        context['selected_lang'] = selected_lang

        # Добавляем параметры запроса для пагинации
        query_dict = self.request.GET.copy()
        query_dict.pop('page', None)
        context['query_params'] = query_dict.urlencode()

        return context


class TableViewId(LoginRequiredMixin, DetailView):
    """
    Описание таблиц
    """

    model = Table
    template_name = 'dba/tables-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.object
        context['column'] = (Column.objects
                             .filter(table=table)
                             .filter(is_active=True)
                             .order_by('date_create', 'id'))
        context['stage'] = (StageColumn.objects
                            .filter(column_id__in=context['column'])
                            .filter(is_active=True))
        context['column_column'] = (ColumnColumn.objects
                                    .filter(main_id__in=context['column'])
                                    .filter(is_active=True))
        context['update_column'] = (Update.objects
                                    .filter(pk__in=ColumnColumn.objects
                                            .filter(main_id__in=context['column'])
                                            .exclude(update_id__isnull=True)
                                            .values('update_id')
                                            .distinct()))
        context['service'] = (Service.objects
                              .filter(pk__in=ServiceTable.objects
                                      .filter(table_id=table.id)
                                      .filter(is_active=True)
                                      .values('service_id')
                                      .distinct()))
        return context


class ColumnView(LoginRequiredMixin, FilteredListView):
    """
    Отображение списка столбцов таблиц базы данных
    """

    template_name = 'dba/columns.html'
    model = Column
    filter_class = ColumnFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем текущие параметры GET
        query_dict = self.request.GET.copy()
        # Удаляем параметр 'page'
        query_dict.pop('page', None)
        context['query_params'] = query_dict.urlencode()  # Передаем строку запроса в контекст
        return context


class UpdateView(LoginRequiredMixin, FilteredListView):
    """
    Расписание обновлений.
    """

    template_name = 'dba/update.html'
    model = Update
    filter_class = UpdateFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # Применяем get_cron к каждому элементу schedule
        for update in queryset:
            if update.schedule:  # Проверяем, что schedule не пустое
                try:
                    update.my_schedule = get_cron(update.schedule)
                except ValueError as e:
                    # Обработайте ошибку, если cron-выражение некорректно
                    update.my_schedule = 'Некорректное cron выражение'  # или другое значение по умолчанию
            else:
                update.my_schedule = 'Нет расписания'  # или другое значение по умолчанию
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущие параметры GET
        query_dict = self.request.GET.copy()
        query_dict.pop('page', None)  # Удаляем параметр 'page'
        context['query_params'] = query_dict.urlencode()  # Передаем строку запроса в контекст
        return context


class UpdateViewId(LoginRequiredMixin, DetailView):
    """
    Расписание обновлений. Список отдельных
    """

    model = Update
    template_name = 'dba/updates-detail.html'
    context_object_name = 'update'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['column_column'] = ColumnColumn.objects.filter(update_id=self.object.id)
        return context


class TableViewIdStage(LoginRequiredMixin, View):
    """

    """

    def get(self, request: HttpRequest) -> HttpResponse:
        filter = StageColumnFilter(request.GET, queryset=StageColumn.objects.filter(is_active=True))
        # пагинатор
        paginator_filter = Paginator(filter.qs, 200)
        page_number = request.GET.get('page')
        person_page_odj = paginator_filter.get_page(page_number)
        context = {
            'title': 'Table',
            'filter': filter,
            'person_page_odj': person_page_odj
        }
        return render(request, 'dba/tables-detail.html', context=context)


class TableViewIdStageId(LoginRequiredMixin, DetailView):
    """
    Таблица
    """

    model = Table
    template_name = 'dba/tables-detail.html'
    context_object_name = 'table'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column_list = Column.objects.filter(table=self.object.pk)
        filter_qs = StageColumn.objects.filter(column_id__in=column_list).filter(is_active=True)
        self.filter_set = self.filterset_class(self.request.GET, queryset=filter_qs)
        paginator = Paginator(self.filter_set.qs, 200)
        page_number = self.request.GET.get('page')
        person_page_odj = paginator.get_page(page_number)
        context['filter'] = self.filter_set
        context['person_page_odj'] = person_page_odj
        return context


class ServiceView(LoginRequiredMixin, FilteredListView):
    """
    Список сервисов
    """

    template_name = 'dba/services.html'
    model = Service
    filter_class = ServiceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем текущие параметры GET
        query_dict = self.request.GET.copy()
        # Удаляем параметр 'page'
        query_dict.pop('page', None)
        context['query_params'] = query_dict.urlencode()  # Передаем строку запроса в контекст
        return context


class ServiceViewId(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'dba/services-detail.html'
    context_object_name = 'service'
    paginate_by = 10  # Количество элементов на странице

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_tables = ServiceTable.objects.filter(
            service_id=self.object.pk,
            is_active=True
        ).select_related('table', 'table__schema', 'table__schema__base')

        paginator = Paginator(service_tables, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['service_tables'] = page_obj.object_list  # Изменено на object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()  # Добавлен флаг пагинации
        return context