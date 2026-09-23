from app.database import get_connection


def get_database_schema():

    query = """
    Retrieve detailed database schema metadata.

    Includes:
    - tables
    -columns
    -data types
    -primary keys
    -foreign keys
    -relationships
    """
    schema = {}

    # Get TABLES and COLUMNS

    column_query = """
    SELECT
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable
    FROM information_schema.columns c
    WHERE c.table_schema = 'public'
    ORDER BY 
        c.table_name,
        c.ordinal_position
    """

    # GET PRIMARY KEY
    primary_key_query = """
    SELECT 
        kcu.table_name,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE 
        tc.table_schema = 'public'
        AND tc.constraint_type = 'PRIMARY KEY'
    """

    # GET FOREIGN KEYS
    foreign_key_query = """
    SELECT
        kcu.table_name,
        kcu.column_name,
        ccu.table_name AS referenced_table,
        ccu.column_name AS referenced_column
    FROM information_schema.key_column_usage kcu
    JOIN information_schema.table_constraints tc
        ON kcu.constraint_name = tc.constraint_name
        AND kcu.table_schema = tc.table_schema
    JOIN information_schema.constraint_column_usage ccu
        ON kcu.constraint_name = ccu.constraint_name
        AND tc.table_schema = ccu.table_schema
    WHERE
        tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'; 
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(column_query)
            column_rows = cursor.fetchall()

            cursor.execute(primary_key_query)
            primary_key_rows = cursor.fetchall()

            cursor.execute(foreign_key_query)
            foreign_key_rows = cursor.fetchall()



    for (table, column, data_type, nullable) in column_rows:

        if table not in schema:
            schema[table] = {
                "columns": [],
                "primary_keys": [],
                "foreign_keys": []
            }

        schema[table]["columns"].append({
            'column': column,
            'type': data_type,
            "nullable": nullable
        })
    
    for table, column in primary_key_rows:

        if table in schema:
            schema[table]["primary_keys"].append(column)
    
    for(table, column, referenced_table, referenced_column) in foreign_key_rows:

        if table in schema:
            schema[table]["foreign_keys"].append({
                "column": column,
                "reference_table": referenced_table,
                "referenced_column": referenced_column
            })

    return schema
        




