"""
Синхронизация моделей:
1) деактивация
2) активация
3) добавление
"""

from django.db import connection, transaction


def sync_database(name_db, stage_db):
    if not name_db or not stage_db:
        return "Ошибка: name_db или stage_db пустой"

    try:
        with connection.cursor() as cursor:
            # 🔹 Получаем все строки TotalData для этой базы и слоя
            cursor.execute("""
                SELECT 
                    schem_name, schem_description,
                    tab_type, tab_is_metadata, tab_name, tab_description,
                    col_type, col_columns, col_is_null, col_is_key, col_unique_together, col_default, col_description,
                    col_date_create
                FROM my_dbmatch.link_total_data
                WHERE is_active = TRUE AND db_name = %s AND stage = %s;
            """, [name_db.name, stage_db.name])
            rows = cursor.fetchall()

            if not rows:
                # Если нет активных данных, деактивируем все связанные записи
                with transaction.atomic():
                    cursor.execute("""
                        UPDATE my_dbmatch.link_columns_stage 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE stage_id = (SELECT id FROM my_dbmatch.dim_stage WHERE name = %s);
                    """, [stage_db.name])

                    cursor.execute("""
                        UPDATE my_dbmatch.link_columns 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE table_id IN (
                            SELECT lt.id FROM my_dbmatch.link_tables lt
                            JOIN my_dbmatch.link_base_schemas lbs ON lt.schema_id = lbs.id
                            JOIN my_dbmatch.dim_db db ON lbs.base_id = db.id
                            WHERE db.name = %s
                        );
                    """, [name_db.name])

                    cursor.execute("""
                        UPDATE my_dbmatch.link_tables 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE schema_id IN (
                            SELECT id FROM my_dbmatch.link_base_schemas 
                            WHERE base_id = (SELECT id FROM my_dbmatch.dim_db WHERE name = %s)
                        );
                    """, [name_db.name])

                    cursor.execute("""
                        UPDATE my_dbmatch.link_base_schemas 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE base_id = (SELECT id FROM my_dbmatch.dim_db WHERE name = %s);
                    """, [name_db.name])

                return "Нет активных данных для синхронизации - все записи деактивированы"

            # Собираем идентификаторы для последующей деактивации отсутствующих записей
            processed_schemas = set()
            processed_tables = set()
            processed_columns = set()

            with transaction.atomic():
                for row in rows:
                    (
                        schem_name, schem_description,
                        tab_type, tab_is_metadata, tab_name, tab_description,
                        col_type, col_columns, col_is_null, col_is_key, col_unique_together, col_default,
                        col_description,
                        col_date_create
                    ) = row

                    # 1. Схема
                    cursor.execute("""
                        INSERT INTO my_dbmatch.link_base_schemas (base_id, "schema", description, is_active, created_at, updated_at)
                        VALUES (
                            (SELECT id FROM my_dbmatch.dim_db WHERE name = %s LIMIT 1),
                            %s, %s, TRUE, NOW(), NOW()
                        )
                        ON CONFLICT (base_id, "schema")
                        DO UPDATE SET description = EXCLUDED.description, is_active = TRUE, updated_at = NOW()
                        RETURNING id;
                    """, [name_db.name, schem_name, schem_description])

                    schema_id = cursor.fetchone()[0]
                    processed_schemas.add(schema_id)

                    # 2. Тип таблицы
                    cursor.execute("""
                        INSERT INTO my_dbmatch.dim_table_type (name, created_at, updated_at, is_active)
                        VALUES (%s, NOW(), NOW(), TRUE)
                        ON CONFLICT (name)
                        DO UPDATE SET updated_at = NOW(), is_active = TRUE
                        RETURNING id;
                    """, [tab_type])

                    table_type_id = cursor.fetchone()[0]

                    # 3. Таблица
                    cursor.execute("""
                        INSERT INTO my_dbmatch.link_tables (schema_id, type_id, name, is_metadata, description, created_at, updated_at, is_active)
                        VALUES (
                            %s, %s, %s, %s, %s, NOW(), NOW(), TRUE
                        )
                        ON CONFLICT (schema_id, type_id, name)
                        DO UPDATE SET description = EXCLUDED.description, is_metadata = EXCLUDED.is_metadata, 
                                      updated_at = NOW(), is_active = TRUE
                        RETURNING id;
                    """, [schema_id, table_type_id, tab_name, tab_is_metadata, tab_description])

                    table_id = cursor.fetchone()[0]
                    processed_tables.add(table_id)

                    # 4. Колонка
                    cursor.execute("""
                        INSERT INTO my_dbmatch.link_columns (table_id, type, columns, is_null, is_key, unique_together, "default", description, date_create, created_at, updated_at, is_active)
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), TRUE
                        )
                        ON CONFLICT (table_id, columns)
                        DO UPDATE SET type = EXCLUDED.type, is_null = EXCLUDED.is_null, is_key = EXCLUDED.is_key,
                                      unique_together = EXCLUDED.unique_together, "default" = EXCLUDED.default,
                                      description = EXCLUDED.description, updated_at = NOW(), is_active = TRUE
                        RETURNING id;
                    """, [table_id, col_type, col_columns, col_is_null, col_is_key,
                          col_unique_together, col_default, col_description, col_date_create])

                    column_id = cursor.fetchone()[0]
                    processed_columns.add(column_id)

                    # 5. Связь колонка ↔ stage
                    stage_id_result = cursor.execute("""
                        SELECT id FROM my_dbmatch.dim_stage WHERE name = %s;
                    """, [stage_db.name])
                    stage_id = cursor.fetchone()[0]

                    cursor.execute("""
                        INSERT INTO my_dbmatch.link_columns_stage (stage_id, column_id, created_at, updated_at, is_active)
                        VALUES (%s, %s, NOW(), NOW(), TRUE)
                        ON CONFLICT (stage_id, column_id)
                        DO UPDATE SET updated_at = NOW(), is_active = TRUE;
                    """, [stage_id, column_id])

                # 🔹 Деактивируем записи, которые отсутствуют в исходных данных

                # Деактивируем схемы
                if processed_schemas:
                    cursor.execute("""
                        UPDATE my_dbmatch.link_base_schemas 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE base_id = (SELECT id FROM my_dbmatch.dim_db WHERE name = %s)
                        AND id NOT IN %s;
                    """, [name_db.name, tuple(processed_schemas)])

                # Деактивируем таблицы
                if processed_tables:
                    cursor.execute("""
                        UPDATE my_dbmatch.link_tables 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE schema_id IN (
                            SELECT id FROM my_dbmatch.link_base_schemas 
                            WHERE base_id = (SELECT id FROM my_dbmatch.dim_db WHERE name = %s)
                        )
                        AND id NOT IN %s;
                    """, [name_db.name, tuple(processed_tables)])

                # Деактивируем колонки
                if processed_columns:
                    cursor.execute("""
                        UPDATE my_dbmatch.link_columns 
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE table_id IN (
                            SELECT id FROM my_dbmatch.link_tables 
                            WHERE schema_id IN (
                                SELECT id FROM my_dbmatch.link_base_schemas 
                                WHERE base_id = (SELECT id FROM my_dbmatch.dim_db WHERE name = %s)
                            )
                        )
                        AND id NOT IN %s;
                    """, [name_db.name, tuple(processed_columns)])

                # Деактивируем связи колонок со stage
                cursor.execute("""
                    UPDATE my_dbmatch.link_columns_stage 
                    SET is_active = FALSE, updated_at = NOW()
                    WHERE stage_id = (SELECT id FROM my_dbmatch.dim_stage WHERE name = %s)
                    AND column_id NOT IN %s;
                """, [stage_db.name, tuple(processed_columns) if processed_columns else (0,)])

            return f"Синхронизировано {len(rows)} строк. Деактивированы отсутствующие записи."

    except Exception as error:
        return f"Ошибка: {error}"
