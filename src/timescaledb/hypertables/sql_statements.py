# SQL statements for TimescaleDB hypertable operations
LIST_HYPERTABLES_SQL = """
SELECT * FROM timescaledb_information.hypertables;
"""

CREATE_HYPERTABLE_SQL = """
SELECT create_hypertable(
    :table_name, 
    by_range(:time_field, INTERVAL :time_interval),
    if_not_exists => :if_not_exists,
    migrate_data => :migrate_data
);
"""

ENABLE_COMPRESSION_SQL = """
ALTER TABLE :table_name SET (
    timescaledb.compress = on,
    timescaledb.compress_after = :compress_after
    || CASE WHEN :segmentby IS NOT NULL THEN ',timescaledb.compress_segmentby = ' || :segmentby ELSE '' END
    || CASE WHEN :compress_orderby IS NOT NULL THEN ',timescaledb.compress_orderby = ' || :compress_orderby ELSE '' END
    || CASE WHEN :compress_drop_after IS NOT NULL THEN ',timescaledb.compress_drop_after = ' || :compress_drop_after ELSE '' END
);
"""
