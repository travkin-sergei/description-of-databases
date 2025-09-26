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