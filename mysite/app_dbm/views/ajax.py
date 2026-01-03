import logging
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from ..models import LinkDB, LinkSchema, LinkTable, LinkColumn, DimDB



@csrf_protect
def get_schemas(request):
    db_id = request.GET.get('db_id')
    logger.info(f"[get_schemas] Получен db_id: {db_id}")

    if not db_id or not db_id.isdigit():
        logger.warning(f"[get_schemas] db_id невалидный: {db_id}")
        return JsonResponse([], status=400)

    try:
        schemas = list(LinkSchema.objects.filter(base_id=int(db_id)).values('id', 'schema'))
        logger.info(f"[get_schemas] Найденные схемы: {schemas}")
        if not schemas:
            return JsonResponse({"error": "Схемы не найдены"}, status=404)
        return JsonResponse(schemas, safe=False)
    except Exception as e:
        logger.error(f"[get_schemas] Ошибка: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_protect
def get_tables(request):
    schema_id = request.GET.get('schema_id')
    if not schema_id or not schema_id.isdigit():
        return JsonResponse([], status=400)


    tables = list(LinkTable.objects.filter(schema_id=int(schema_id)).values('id', 'name'))
    if not tables:
        return JsonResponse({"error": "Таблицы не найдены"}, status=404)


    return JsonResponse(tables, safe=False)


@csrf_protect
def get_columns(request):
    table_id = request.GET.get('table_id')
    if not table_id or not table_id.isdigit():
        return JsonResponse([], status=400)


    columns = list(LinkColumn.objects.filter(table_id=int(table_id)).values('id', 'columns', 'type'))
    if not columns:
        return JsonResponse({"error": "Столбцы не найдены"}, status=404)


    return JsonResponse(columns, safe=False)


def linked_form_view(request):
    databases = DimDB.objects.all()
    return render(request, 'app_dbm/linked_form.html', {'databases': databases})
