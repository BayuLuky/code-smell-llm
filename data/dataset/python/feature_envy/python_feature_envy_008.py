def get_table_description(self, cursor, table_name):
    """
    Return a description of the table with the DB-API cursor.description
    interface.
    """
    # Query the pg_catalog tables as cursor.description does not reliably
    # return the nullable property and information_schema.columns does not
    # contain details of materialized views.
    cursor.execute(
        """
        SELECT
            a.attname AS column_name,
            NOT (a.attnotnull OR (t.typtype = 'd' AND t.typnotnull)) AS is_nullable,
            pg_get_expr(ad.adbin, ad.adrelid) AS column_default,
            CASE WHEN collname = 'default' THEN NULL ELSE collname END AS collation,
            a.attidentity != '' AS is_autofield,
            col_description(a.attrelid, a.attnum) AS column_comment
        FROM pg_attribute a
        LEFT JOIN pg_attrdef ad ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
        LEFT JOIN pg_collation co ON a.attcollation = co.oid
        JOIN pg_type t ON a.atttypid = t.oid
        JOIN pg_class c ON a.attrelid = c.oid
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE c.relkind IN ('f', 'm', 'p', 'r', 'v')
            AND c.relname = %s
            AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
            AND pg_catalog.pg_table_is_visible(c.oid)
    """,
        [table_name],
    )
    field_map = {line[0]: line[1:] for line in cursor.fetchall()}
    cursor.execute(
        "SELECT * FROM %s LIMIT 1" % self.connection.ops.quote_name(table_name)
    )
    return [
        FieldInfo(
            line.name,
            line.type_code,
            # display_size is always None on psycopg2.
            line.internal_size if line.display_size is None else line.display_size,
            line.internal_size,
            line.precision,
            line.scale,
            *field_map[line.name],
        )
        for line in cursor.description
    ]
