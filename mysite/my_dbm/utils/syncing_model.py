# utils/syncing_model.py
"""
Синхронизация моделей:
1) деактивация
2) активация
3) добавление
"""
# utils/syncing_model.py
import logging
from django.db import connection, transaction
from contextlib import closing
import time

logger = logging.getLogger(__name__)


def sync_database(name_db, stage_db):
    """
    Массовая синхронизация для миллионов записей
    """
    start_time = time.time()
    name_db = name_db.name
    stage_db = stage_db.name

    sql_insert = [
        # 1. Добавляем недостающие данные schemas
        """
        INSERT INTO my_dbmatch.link_base_schemas(created_at, updated_at, is_active, schema, description, base_id)
        SELECT
             NOW()                 AS created_at
            ,NOW()                 AS updated_at
            ,TRUE                  AS is_active
            ,ltd.schem_name        AS schema
            ,ltd.schem_description AS schem_description
            ,ldb.base_id           AS schem_name_id
        FROM my_dbmatch.link_total_data AS ltd
            LEFT JOIN my_dbmatch.dim_stage         AS dst ON dst.name = ltd.stage
            LEFT JOIN my_dbmatch.link_db           AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
            LEFT JOIN my_dbmatch.link_base_schemas AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
        WHERE 1=1
            AND lbs.id IS NULL
            AND ltd.stage = %s
            AND ltd.db_name = %s
        """,

        # 2. Добавляем недостающие данные table
        """
        INSERT INTO my_dbmatch.link_tables(created_at, updated_at, is_active, is_metadata, name, description, schema_id, type_id)
        SELECT
             NOW()               AS created_at
            ,NOW()               AS updated_at
            ,TRUE                AS is_active
            ,ltd.tab_is_metadata AS is_metadata
            ,ltd.tab_name        AS name
            ,ltd.tab_description AS description
            ,lbs.id              AS schema_id
            ,dtt.id              AS type_id
        FROM my_dbmatch.link_total_data AS ltd
            LEFT JOIN my_dbmatch.dim_stage         AS dst ON dst.name = ltd.stage
            LEFT JOIN my_dbmatch.link_db           AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
            LEFT JOIN my_dbmatch.link_base_schemas AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
            LEFT JOIN my_dbmatch.dim_table_type    AS dtt ON dtt.name = ltd.tab_type
            LEFT JOIN my_dbmatch.link_tables       AS lts ON lts.type_id = dtt.id AND lts.schema_id = lbs.id AND lts.name = ltd.tab_name
        WHERE 1=1
            AND lts.id IS NULL
            AND ltd.stage = %s
            AND ltd.db_name = %s
        """,

        # 3. Добавляем недостающие столбцы
        """
        INSERT INTO my_dbmatch.link_columns(
            created_at, updated_at, is_active, date_create, type, columns, is_null, is_key, unique_together, "default", description, table_id)
        SELECT 
             NOW()                   AS created_at
            ,NOW()                   AS updated_at
            ,TRUE                    AS is_active
            ,ltd.col_date_create     AS date_create
            ,ltd.col_type            AS type
            ,ltd.col_columns         AS columns
            ,ltd.col_is_null         AS is_null
            ,ltd.col_is_key          AS is_key
            ,ltd.col_unique_together AS unique_together
            ,ltd.col_default         AS "default"
            ,ltd.col_description     AS description
            ,lts.id                  AS table_id
        FROM my_dbmatch.link_total_data AS ltd
            LEFT JOIN my_dbmatch.dim_stage         AS dst ON dst.name = ltd.stage
            LEFT JOIN my_dbmatch.link_db           AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
            LEFT JOIN my_dbmatch.link_base_schemas AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
            LEFT JOIN my_dbmatch.dim_table_type    AS dtt ON dtt.name = ltd.tab_type
            LEFT JOIN my_dbmatch.link_tables       AS lts ON lts.type_id = dtt.id AND lts.schema_id = lbs.id AND lts.name = ltd.tab_name
            LEFT JOIN my_dbmatch.link_columns      AS lcs ON lcs.columns = ltd.col_columns AND lcs.table_id = lts.id
        WHERE 1=1
            AND lcs.id      IS NULL
            AND ltd.stage   = %s
            AND ltd.db_name = %s
        """,

        # 4. Добавляем данные в stage
        """
        INSERT INTO my_dbmatch.link_columns_stage(created_at, updated_at, is_active, column_id, stage_id)
        SELECT 
             NOW() AS created_at
            ,NOW() AS updated_at
            ,TRUE AS is_active
            ,lcs.id AS column_id
            ,dst.id AS stage_id
        FROM my_dbmatch.link_total_data AS ltd
            LEFT JOIN my_dbmatch.dim_stage          AS dst ON dst.name = ltd.stage
            LEFT JOIN my_dbmatch.link_db            AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
            LEFT JOIN my_dbmatch.link_base_schemas  AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
            LEFT JOIN my_dbmatch.dim_table_type     AS dtt ON dtt.name = ltd.tab_type
            LEFT JOIN my_dbmatch.link_tables        AS lts ON lts.type_id = dtt.id AND lts.schema_id = lbs.id AND lts.name = ltd.tab_name
            LEFT JOIN my_dbmatch.link_columns       AS lcs ON lcs.columns = ltd.col_columns AND lcs.table_id = lts.id
            LEFT JOIN my_dbmatch.link_columns_stage AS lct ON lct.column_id = lcs.id AND lct.stage_id = dst.id
        WHERE 1=1
            AND lct.id     IS NULL
            AND ltd.stage   = %s
            AND ltd.db_name = %s
        """
    ]

    try:
        with transaction.atomic():
            with closing(connection.cursor()) as cursor:
                # вставляем новые данные
                for sql_query in sql_insert:
                    try:
                        logger.info(f"🔄 Выполнение запроса.")
                        cursor.execute(sql_query, [stage_db, name_db])
                        row_count = cursor.rowcount
                        logger.info(f"✅ Запрос выполнен. Затронуто строк: {row_count}")

                    except Exception as e:
                        logger.error(f"❌ Ошибка в запросе: {str(e)}")
                        # При ошибке транзакция автоматически откатится
                        raise

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"✅ Синхронизация завершена за {execution_time:.2f} секунд")
        return f"Синхронизация завершена за {execution_time:.2f} секунд"

    except Exception as e:
        logger.error(f"❌ Ошибка синхронизации: {str(e)}")
        return f"Ошибка: {str(e)}"
