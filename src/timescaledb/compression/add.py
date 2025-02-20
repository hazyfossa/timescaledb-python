from typing import Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.compression import sql_statements as sql


def add_compression_policy(session: Session, model: Type[SQLModel]) -> None:
    """
    Enable compression for a hypertable
    """
    enable_compression = model.__enable_compression__
    if not enable_compression:
        return

    # Build compression parameters dict with optional parameters
    compression_params = {
        "table_name": model.__tablename__,
        "compress": model.__enable_compression__,
        "compress_orderby": getattr(model, "__compress_orderby__", None),
        "compress_segmentby": getattr(model, "__compress_segmentby__", None),
        "compress_chunk_time_interval": getattr(
            model, "__compress_chunk_time_interval__", None
        ),
    }
    # Use the SQL statement from sql_statements.py
    query = sqlalchemy.text(sql.ALTER_COMPRESSION_POLICY_SQL).bindparams(
        **compression_params
    )
    compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))
    session.execute(sqlalchemy.text(compiled_query))
    session.commit()
