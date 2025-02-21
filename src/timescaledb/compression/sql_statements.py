from sqlalchemy.sql import quoted_name


def get_alter_compression_policy_sql(
    table_name: str, with_orderby: bool = True, with_segmentby: bool = True
):
    safe_table_name = quoted_name(table_name, True)

    clauses = []
    if with_orderby:
        clauses.append("timescaledb.compress_orderby = :compress_orderby")
    if with_segmentby:
        clauses.append("timescaledb.compress_segmentby = :compress_segmentby")

    compress_clause = "timescaledb.compress"
    if len(clauses) > 0:
        compress_clause = "timescaledb.compress,"
    # Create the SQL with the safely quoted table name
    sql = f"""
    ALTER TABLE {safe_table_name} SET (
        {compress_clause}
        {", ".join(clauses)}
    );
    """
    return sql
