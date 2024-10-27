from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.db.models import Count

from .filters import *


def page_note_found(request, exception):
    # обработка 404 ошибки отсутствия страницы
    HttpResponseNotFound("<h1>Страница не найдено 404 ошибка</h1>")


# Create your views here.
def defBasesView(request):
    filter = BaseGroupFilter(request.GET, queryset=BaseGroup.objects.all())
    # пагинатор
    paginator_filter = Paginator(filter.qs, 20)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'defBasesView',
        'person_page_odj': person_page_odj,
        'filter': filter
    }
    return render(request, 'dba/defBasesView.html', context=context)


def defBasesView_id(request, base_id):
    base_group = BaseGroup.objects.get(pk=base_id)
    base = Base.objects.filter(base_id=base_id)
    context = {
        'title': 'view_news',
        'base_group': base_group,
        'base': base,
    }
    return render(request, 'dba/a-bout.html', context=context)


def defFunctionView(request):
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
    return render(request, 'dba/defFunctionView.html', context=context)


def defFunctionView_id(request, function_id):
    function = Function.objects.get(pk=function_id)
    stage = StageFunction.objects.filter(function_id=function_id).filter(is_active=True)
    context = {
        'title': 'defFunctionView_id',
        'function': function,
        'stage': stage,
    }
    return render(request, 'dba/defFunctionView_id.html', context=context)


def defTableView(request):
    filter = TableFilter(request.GET, queryset=Table.objects.filter(is_metadata=False))
    # count = Column.objects.annotate(column_id=Count('column_id')).values('id', 'column_count')

    # пагинатор
    paginator_filter = Paginator(filter.qs, 20)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'defTableView',
        'person_page_odj': person_page_odj,
        'filter': filter,
        # 'count': count,
    }
    return render(request, 'dba/defTableView.html', context=context)


def defTableView_id(request, table_id):
    table = Table.objects.get(pk=table_id)
    column = Column.objects.filter(table=table_id).order_by('date_create', 'id')
    list_column = Column.objects.filter(table=table_id)
    stage = StageColumn.objects.filter(column_id__in=list_column).filter(is_active=True)
    column_column = ColumnColumn.objects.filter(main_id__in=list_column).filter(is_active=True)
    # -------------- -------------- -------------- -------------- --------------
    update_id = ColumnColumn.objects.filter(main_id__in=list_column).exclude(update_id__isnull=True).values(
        'update_id').distinct()
    update_column = Update.objects.filter(pk__in=update_id)
    # -------------- -------------- -------------- -------------- --------------
    service_id = ServiceTable.objects.filter(table_id=table_id).filter(is_active=True).values('service_id').distinct()
    service = Service.objects.filter(pk__in=service_id)
    # -------------- -------------- -------------- -------------- --------------
    context = {
        'title': 'Table',
        'table': table,
        'column': column,
        'stage': stage,
        'column_column': column_column,
        'update_column': update_column,
        'service': service,
    }
    return render(request, 'dba/defTableView_id.html', context=context)


def defColumnView(request):
    filter = ColumnFilter(request.GET, queryset=Column.objects.filter(is_active=True))
    # пагинатор
    paginator_filter = Paginator(filter.qs, 20)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'defColumnView',
        'person_page_odj': person_page_odj,
        'filter': filter
    }
    return render(request, 'dba/defColumnView.html', context=context)


def defUpdateView(request):
    """Расисание обновлений. Список всех"""
    filter = UpdateFilter(request.GET, queryset=Update.objects.all())
    # пагинатор
    paginator_filter = Paginator(filter.qs, 20)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'Обновления',
        'filter': filter,
        'person_page_odj': person_page_odj
    }
    return render(request, 'dba/defUpdateView.html', context=context)


def defUpdateView_id(request, update_id):
    """Расисание обновлений. Список отдельных"""
    filter = UpdateFilter(request.GET, queryset=Update.objects.filter(id=update_id))
    # Расписание обновлений
    update = Update.objects.filter(id=update_id).filter(is_active=True)
    # Обнолвяемые столбцы
    column_column = ColumnColumn.objects.filter(update_id=update_id)  # .filter(is_active=True).filter(type='filling')
    # Данные

    # пагинация
    paginator_filter = Paginator(filter.qs, 20)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'defUpdateView_id',
        'person_page_odj': person_page_odj,
        'filter': filter,
        'update': update,
        'column_column': column_column,
    }
    return render(request, 'dba/defUpdateView_id.html', context=context)


def defTableView_id_stage(request):
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
    return render(request, 'dba/defTableView_id_stage.html', context=context)


def defTableView_id_stage_id(request, stage_ig):
    table = Table.objects.get(pk=stage_ig)
    column_list = Column.objects.filter(table=stage_ig)
    filter = StageColumnFilter(request.GET,
                               queryset=StageColumn.objects.filter(column_id__in=column_list).filter(is_active=True))
    # пагинатор
    paginator_filter = Paginator(filter.qs, 200)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'Table',
        'table': table,
        'filter': filter,
        'person_page_odj': person_page_odj
    }
    return render(request, 'dba/defTableView_id_stage.html', context=context)


def defServiceView(request):
    filter = ServiceFilter(request.GET, queryset=Service.objects.filter(is_active=True))
    # пагинатор
    paginator_filter = Paginator(filter.qs, 20)
    page_number = request.GET.get('page')
    person_page_odj = paginator_filter.get_page(page_number)
    context = {
        'title': 'defServiceView',
        'person_page_odj': person_page_odj,
        'filter': filter
    }
    return render(request, 'dba/defServiceView.html', context=context)


def defServiceView_id(request, service_id):
    service = Service.objects.get(pk=service_id)
    table = ServiceTable.objects.filter(service_id=service_id).filter(is_active=True)
    context = {
        'title': 'defServiceView_id',
        'service': service,
        'table': table,
    }
    return render(request, 'dba/defServiceView_id.html', context=context)
