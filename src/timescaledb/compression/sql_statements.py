ALTER_COMPRESSION_POLICY_SQL = """
ALTER TABLE :table_name SET (
        timescaledb.compress = :compress,
        timescaledb.compress_orderby = NULLIF(:compress_orderby, NULL),
        timescaledb.compress_segmentby = NULLIF(:compress_segmentby, NULL),
        timescaledb.compress_chunk_time_interval = NULLIF(:compress_chunk_time_interval, NULL)
    );
"""
