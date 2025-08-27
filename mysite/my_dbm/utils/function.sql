WITH
table_metadata AS (
    SELECT
        (table_schema || '.' || table_name)::regclass::oid AS table_oid,
        table_catalog AS db_name,
        table_schema AS db_schema,
        table_name AS db_table,
        table_type AS table_type
    FROM information_schema.tables
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
)
,constraint_info AS (
    SELECT
        (conrelid, conkey) AS oid_col,
        MAX(CASE WHEN contype = 'p' THEN 'YES' END) AS is_primary_key
    FROM (
        SELECT
            conrelid AS conrelid,
            UNNEST(conkey) AS conkey,
            contype AS contype
        FROM pg_constraint
    ) AS unnested_constraints
    GROUP BY oid_col
)
,foreign_key_info AS (
    SELECT
        (c.conrelid, c.conkey[1]) AS oid_col,
        'Ссылка на ' || referenced_table.relname || ' столбец ' || referenced_column.column_name AS description
    FROM pg_constraint AS c
    JOIN pg_class AS source_table ON source_table.oid = c.conrelid
    JOIN pg_class AS referenced_table ON referenced_table.oid = c.confrelid
    JOIN information_schema.columns AS referenced_column ON 1=1
        AND referenced_column.table_name = referenced_table.relname
        AND c.confkey[1] = referenced_column.ordinal_position
    WHERE c.contype = 'f'
)
,column_info AS (
    SELECT
        c.table_catalog
        ,c.table_schema
        ,c.ordinal_position
        ,(c.table_schema  || '.' || c.table_name)::regclass::oid AS table_oid
        ,((c.table_schema || '.' || c.table_name)::regclass::oid
        , c.ordinal_position) AS oid_col
        ,c.table_name
        ,obj_description((c.table_schema || '.' || c.table_name)::regclass::oid) AS table_comment
        ,c.column_name
        ,col_description((c.table_schema || '.' || c.table_name)::regclass::oid, c.ordinal_position) AS column_comment
        ,CASE
            WHEN c.udt_name = 'varchar' THEN COALESCE(c.udt_name || '(' || c.character_maximum_length || ')', c.udt_name)
            WHEN c.data_type = 'ARRAY' THEN 'ARRAY'
            ELSE c.udt_name
        END AS data_type
        ,c.is_nullable = 'YES'   AS is_nullable
        ,c.column_default        AS column_default
        ,c.generation_expression AS generation_expression
    FROM information_schema.columns AS c
    WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
)
,db_metadata AS (
    SELECT
        d.datname AS db_name,
        shobj_description(d.oid, 'pg_database') AS db_description
    FROM pg_database d
    WHERE d.datname = current_database()
)
,schema_metadata AS (
    SELECT
        n.nspname AS schema_name,
        obj_description(n.oid, 'pg_namespace') AS schema_description
    FROM pg_namespace n
    WHERE n.nspname NOT LIKE 'pg_%'
    AND n.nspname != 'information_schema'
)
,clean_comment AS (
    SELECT
        ci.*,
        -- Очистка комментария от невалидных JSON символов
        CASE
            WHEN ci.column_comment IS NULL OR ci.column_comment = '' THEN NULL
            WHEN ci.column_comment ~ '^\{.*\}$' THEN ci.column_comment
            ELSE REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        ci.column_comment,
                        '[\\x00-\\x1F\\x7F]', ' ', 'g' -- Удаляем управляющие символы
                    ),
                    '["\\]', '\\\0', 'g' -- Экранируем кавычки и обратные слеши
                ),
                '[\n\r\t]+', ' ', 'g' -- Заменяем переносы и табы на пробелы
            )
        END AS cleaned_comment
    FROM column_info ci
)
SELECT
    'TST'             AS stage
    ,version()        AS db_version
    ,ci.table_catalog AS db_name
    ,(SELECT db_description FROM db_metadata WHERE db_name = ci.table_catalog) AS db_description
    ,ci.table_schema  AS schem_name
    ,(SELECT schema_description FROM schema_metadata WHERE schema_name = ci.table_schema) AS schem_description
    ,false            AS tab_is_metadata
    ,tm.table_type    AS tab_type
    ,ci.table_name    AS tab_name
    ,ci.table_comment AS tab_description
    ,now() AS col_date_create
    ,ci.data_type     AS col_type,ci.column_name AS col_columns
    ,ci.is_nullable   AS col_is_null
    ,CASE WHEN cn.is_primary_key = 'YES' THEN true ELSE false END AS col_is_key
    ,null              AS col_unique_together
    ,ci.column_default AS col_default
    ,CASE
        WHEN ci.cleaned_comment IS NULL THEN '{"name": null}'::jsonb
        WHEN ci.cleaned_comment ~ '^\{.*\}$' THEN ci.cleaned_comment::jsonb
        ELSE ('{"name":"' || ci.cleaned_comment || '"}')::jsonb
    END AS col_description
FROM clean_comment AS ci
    LEFT JOIN foreign_key_info fk ON fk.oid_col::text = ci.oid_col::text
    LEFT JOIN constraint_info cn ON cn.oid_col::text = ci.oid_col::text
    LEFT JOIN table_metadata tm ON tm.table_oid = ci.table_oid
ORDER BY ci.oid_col;




CREATE OR REPLACE FUNCTION my_dbmatch.sync_database(stage_db text, name_db text)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- 1. Добавляем новые схемы
    INSERT INTO my_dbmatch.link_base_schemas(created_at, updated_at, is_active, schema, description, base_id)
    SELECT NOW(), NOW(), TRUE, ltd.schem_name, ltd.schem_description, ldb.base_id
    FROM my_dbmatch.link_total_data AS ltd
        LEFT JOIN my_dbmatch.dim_stage         AS dst ON dst.name = ltd.stage
        LEFT JOIN my_dbmatch.link_db           AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
        LEFT JOIN my_dbmatch.link_base_schemas AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
    WHERE lbs.id IS NULL
      AND ltd.stage = stage_db
      AND ltd.db_name = name_db;

    -- 2. Таблицы
    INSERT INTO my_dbmatch.link_tables(created_at, updated_at, is_active, is_metadata, name, description, schema_id, type_id)
    SELECT NOW(), NOW(), TRUE, ltd.tab_is_metadata, ltd.tab_name, ltd.tab_description, lbs.id, dtt.id
    FROM my_dbmatch.link_total_data AS ltd
        LEFT JOIN my_dbmatch.dim_stage         AS dst ON dst.name = ltd.stage
        LEFT JOIN my_dbmatch.link_db           AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
        LEFT JOIN my_dbmatch.link_base_schemas AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
        LEFT JOIN my_dbmatch.dim_table_type    AS dtt ON dtt.name = ltd.tab_type
        LEFT JOIN my_dbmatch.link_tables       AS lts ON lts.type_id = dtt.id AND lts.schema_id = lbs.id AND lts.name = ltd.tab_name
    WHERE lts.id IS NULL
      AND ltd.stage = stage_db
      AND ltd.db_name = name_db;

    -- 3. Колонки - ИСПРАВЛЕННЫЙ БЛОК с DISTINCT
    WITH unique_columns AS (
        SELECT DISTINCT ON (lts.id, ltd.col_columns)
            NOW() as created_at,
            NOW() as updated_at,
            TRUE as is_active,
            ltd.col_date_create,
            ltd.col_type,
            ltd.col_columns,
            ltd.col_is_null,
            ltd.col_is_key,
            ltd.col_unique_together,
            ltd.col_default,
            ltd.col_description,
            lts.id as table_id
        FROM my_dbmatch.link_total_data AS ltd
            LEFT JOIN my_dbmatch.dim_stage         AS dst ON dst.name = ltd.stage
            LEFT JOIN my_dbmatch.link_db           AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
            LEFT JOIN my_dbmatch.link_base_schemas AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
            LEFT JOIN my_dbmatch.dim_table_type    AS dtt ON dtt.name = ltd.tab_type
            LEFT JOIN my_dbmatch.link_tables       AS lts ON lts.type_id = dtt.id AND lts.schema_id = lbs.id AND lts.name = ltd.tab_name
        WHERE ltd.stage = stage_db
          AND ltd.db_name = name_db
          AND lts.id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM my_dbmatch.link_columns lcs 
              WHERE lcs.table_id = lts.id AND lcs.columns = ltd.col_columns
          )
    )
    INSERT INTO my_dbmatch.link_columns(
        created_at, updated_at, is_active, date_create, type, columns, is_null, is_key, 
        unique_together, "default", description, table_id)
    SELECT 
        created_at, updated_at, is_active, col_date_create, col_type, col_columns, 
        col_is_null, col_is_key, col_unique_together, col_default, col_description, table_id
    FROM unique_columns
    ON CONFLICT (table_id, columns) 
    DO UPDATE SET
        updated_at = NOW(),
        is_active = TRUE,
        date_create = EXCLUDED.date_create,
        type = EXCLUDED.type,
        is_null = EXCLUDED.is_null,
        is_key = EXCLUDED.is_key,
        unique_together = EXCLUDED.unique_together,
        "default" = EXCLUDED."default",
        description = EXCLUDED.description;

    -- 4. Привязка колонок к stage
    WITH unique_column_stages AS (
        SELECT DISTINCT ON (lcs.id, dst.id)
            NOW() as created_at,
            NOW() as updated_at,
            TRUE as is_active,
            lcs.id as column_id,
            dst.id as stage_id
        FROM my_dbmatch.link_total_data AS ltd
            JOIN my_dbmatch.dim_stage          AS dst ON dst.name = ltd.stage
            JOIN my_dbmatch.link_db            AS ldb ON ldb.stage_id = dst.id AND ldb.alias = ltd.db_name
            JOIN my_dbmatch.link_base_schemas  AS lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
            JOIN my_dbmatch.dim_table_type     AS dtt ON dtt.name = ltd.tab_type
            JOIN my_dbmatch.link_tables        AS lts ON lts.type_id = dtt.id AND lts.schema_id = lbs.id AND lts.name = ltd.tab_name
            JOIN my_dbmatch.link_columns       AS lcs ON lcs.columns = ltd.col_columns AND lcs.table_id = lts.id
        WHERE ltd.stage = stage_db
          AND ltd.db_name = name_db
          AND NOT EXISTS (
              SELECT 1 FROM my_dbmatch.link_columns_stage lct 
              WHERE lct.column_id = lcs.id AND lct.stage_id = dst.id
          )
    )
    INSERT INTO my_dbmatch.link_columns_stage(created_at, updated_at, is_active, column_id, stage_id)
    SELECT created_at, updated_at, is_active, column_id, stage_id
    FROM unique_column_stages
    ON CONFLICT (column_id, stage_id) 
    DO UPDATE SET
        updated_at = NOW(),
        is_active = TRUE;

    -- 5. Деактивация лишних колонок
    UPDATE my_dbmatch.link_columns_stage lct
    SET is_active = FALSE,
        updated_at = NOW()
    WHERE lct.stage_id = (SELECT id FROM my_dbmatch.dim_stage WHERE name = stage_db)
      AND lct.column_id NOT IN (
          SELECT lcs.id
          FROM my_dbmatch.link_total_data ltd
              JOIN my_dbmatch.link_db ldb ON ldb.alias = ltd.db_name
              JOIN my_dbmatch.link_base_schemas lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
              JOIN my_dbmatch.link_tables lts ON lts.schema_id = lbs.id AND lts.name = ltd.tab_name
              JOIN my_dbmatch.link_columns lcs ON lcs.table_id = lts.id AND lcs.columns = ltd.col_columns
          WHERE ltd.stage = stage_db AND ltd.db_name = name_db
      );

    -- 6. Активация связанных
    UPDATE my_dbmatch.link_columns_stage
    SET is_active = TRUE,
        updated_at = NOW()
    WHERE column_id IN (
        SELECT lcs.id
        FROM my_dbmatch.link_columns lcs
            JOIN my_dbmatch.link_tables lts ON lts.id = lcs.table_id
            JOIN my_dbmatch.link_base_schemas lbs ON lbs.id = lts.schema_id
            JOIN my_dbmatch.link_db ldb ON ldb.base_id = lbs.base_id
            JOIN my_dbmatch.dim_stage dst ON dst.id = ldb.stage_id
        WHERE dst.name = stage_db AND ldb.alias = name_db
    );

    UPDATE my_dbmatch.link_columns
    SET is_active = TRUE,
        updated_at = NOW()
    WHERE id IN (SELECT column_id FROM my_dbmatch.link_columns_stage WHERE is_active = TRUE);

    UPDATE my_dbmatch.link_tables
    SET is_active = TRUE,
        updated_at = NOW()
    WHERE id IN (SELECT DISTINCT table_id FROM my_dbmatch.link_columns WHERE is_active = TRUE);

    UPDATE my_dbmatch.link_base_schemas
    SET is_active = TRUE,
        updated_at = NOW()
    WHERE id IN (SELECT DISTINCT schema_id FROM my_dbmatch.link_tables WHERE is_active = TRUE);

END;
$function$
;
