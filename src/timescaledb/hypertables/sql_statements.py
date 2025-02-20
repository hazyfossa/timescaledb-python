CREATE_HYPERTABLE_SQL = """
SELECT create_hypertable(
    :table_name, 
    by_range(:time_field, INTERVAL :time_interval),
    if_not_exists => :if_not_exists,
    migrate_data => :migrate_data
);
"""

LIST_AVAILABLE_HYPERTABLES_SQL = """
SELECT * FROM timescaledb_information.hypertables;
"""
