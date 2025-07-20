# my_dbm/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.sync import sync_schema
from ..models import LinkDBSchema, DimDBTableType, LinkDB


class SyncSchemaAPIView(APIView):
    """
    API endpoint для синхронизации схемы.
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        schema_name = data.get("schema_name")
        tables_data = data.get("tables", [])

        if not schema_name or not tables_data:
            return Response(
                {"detail": "schema_name и tables обязательны."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем host и port из заголовка Host
        host_header = request.headers.get("Host", "")
        if ':' in host_header:
            hostname, port = host_header.split(":", 1)
        else:
            hostname = host_header
            port = ""

        try:
            # 1. Находим LinkDB по host и port
            link_db = LinkDB.objects.get(host=hostname, port=port)

            # 2. Находим схему по имени и связанной базе (DimDB)
            schema = LinkDBSchema.objects.get(
                schema=schema_name,
                base=link_db.data_base  # Используем связь через ForeignKey
            )
        except LinkDB.DoesNotExist:
            return Response(
                {"detail": f"База данных с хостом '{hostname}:{port}' не найдена."},
                status=status.HTTP_404_NOT_FOUND
            )
        except LinkDBSchema.DoesNotExist:
            return Response(
                {"detail": f"Схема '{schema_name}' не найдена для базы данных '{link_db.data_base.name}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Обработка таблиц
        for table_data in tables_data:
            type_name = table_data.get('type_name')
            if not type_name:
                return Response(
                    {"detail": f"type_name обязателен для таблицы {table_data.get('name')}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                table_data['type'] = DimDBTableType.objects.get(name=type_name)
            except DimDBTableType.DoesNotExist:
                return Response(
                    {"detail": f"Тип таблицы '{type_name}' не найден."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Вызов сервиса синхронизации
        sync_schema(schema, tables_data)

        return Response(
            {"detail": "Синхронизация выполнена успешно."},
            status=status.HTTP_200_OK
        )
