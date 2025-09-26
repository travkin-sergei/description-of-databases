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
      AND ltd.stage   = stage_db
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
             NOW()                     as created_at
			,NOW()                     as updated_at
			,TRUE                      as is_active
			,ltd."col_date_create"     as col_date_create
			,ltd."col_type"            as col_type
			,ltd."col_columns"         as col_columns
			,ltd."col_is_null"         as col_is_null
			,ltd."col_is_key"          as col_is_key
			,ltd."col_unique_together" as col_unique_together
			,ltd."col_default"         as col_default
			,ltd."col_description"     as col_description
			,lts."id"                  as table_id
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
        unique_together, "default", description, table_id
    )
    SELECT 
        created_at, updated_at, is_active, col_date_create, col_type, col_columns, 
        col_is_null, col_is_key, col_unique_together, col_default, col_description, table_id
    FROM unique_columns
    ON CONFLICT (table_id, columns) 
    DO UPDATE SET
         "updated_at"      = NOW()
        ,"is_active"       = TRUE
        ,"date_create"     = EXCLUDED."date_create"
        ,"type"            = EXCLUDED."type"
        ,"is_null"         = EXCLUDED."is_null"
        ,"is_key"          = EXCLUDED."is_key"
        ,"unique_together" = EXCLUDED."unique_together"
        ,"default"         = EXCLUDED."default"
        ,"description"     = EXCLUDED."description";

    -- 4. Привязка колонок к stage
    WITH unique_column_stages AS (
        SELECT DISTINCT ON (lcs.id, dst.id)
             NOW()  as created_at
            ,NOW()  as updated_at
            ,TRUE   as is_active
            ,lcs.id as column_id
            ,dst.id as stage_id
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
             updated_at = NOW()
            ,is_active  = TRUE;

-- 5. Деактивация лишних колонок (только если is_active = true)
    UPDATE my_dbmatch.link_columns_stage as lct
    SET is_active = FALSE,
        updated_at = NOW()
	WHERE 1=1
		AND lct.is_active = False
    	AND lct.stage_id = (SELECT id FROM my_dbmatch.dim_stage WHERE name = stage_db )
		AND lct.column_id NOT IN (
          SELECT lcs.id
          FROM my_dbmatch.link_total_data ltd
              JOIN my_dbmatch.link_db ldb ON ldb.alias = ltd.db_name
              JOIN my_dbmatch.link_base_schemas lbs ON lbs.base_id = ldb.base_id AND lbs.schema = ltd.schem_name
              JOIN my_dbmatch.link_tables lts ON lts.schema_id = lbs.id AND lts.name = ltd.tab_name
              JOIN my_dbmatch.link_columns lcs ON lcs.table_id = lts.id AND lcs.columns = ltd.col_columns
          where 1=1
          	AND ltd.stage   = stage_db 
          	AND ltd.db_name = name_db
      );

    -- 6. Активация связанных
    UPDATE my_dbmatch.link_columns_stage
    	set 
    		 is_active = true
    		,updated_at = NOW()
    WHERE 1=1
    	and is_active=FALSE
    	and column_id IN (
        SELECT lcs.id
        FROM my_dbmatch.link_columns lcs
            JOIN my_dbmatch.link_tables lts ON lts.id = lcs.table_id
            JOIN my_dbmatch.link_base_schemas lbs ON lbs.id = lts.schema_id
            JOIN my_dbmatch.link_db ldb ON ldb.base_id = lbs.base_id
            JOIN my_dbmatch.dim_stage dst ON dst.id = ldb.stage_id
        WHERE dst.name = stage_db AND ldb.alias = name_db
    );

    UPDATE my_dbmatch.link_columns
    	set
	    	 is_active = true
			,updated_at = NOW()
    WHERE 1=1
    	and is_active = fALSE
    	and id IN (SELECT column_id FROM my_dbmatch.link_columns_stage WHERE is_active = TRUE);

    UPDATE my_dbmatch.link_tables
    	SET 
    		 is_active = true
    		,updated_at = NOW() 
	WHERE 1=1
		and is_active = fALSE
    	and id IN (SELECT DISTINCT table_id FROM my_dbmatch.link_columns WHERE is_active = TRUE);

    UPDATE my_dbmatch.link_base_schemas
    	SET 
    		 is_active = true
    		,updated_at = NOW()
    WHERE 1=1
		and is_active = false
    	and id IN (SELECT DISTINCT schema_id FROM my_dbmatch.link_tables WHERE is_active = TRUE);

END;
$function$
;
