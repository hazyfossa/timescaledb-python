from typing import Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.compression import sql_statements as sql
from timescaledb.compression.validators import (
    validate_compress_orderby_field,
    validate_compress_segmentby_field,
    validate_unique_segmentby_and_orderby_fields,
)


def add_compression_policy(
    session: Session, model: Type[SQLModel], commit: bool = True, auto_enable=False
) -> None:
    """
    Enable compression for a hypertable
    """
    enable_compression = getattr(model, "__enable_compression__", False)
    enable_compression_bool = str(enable_compression).lower() == "true"
    if not enable_compression_bool:
        return
    compress_orderby = getattr(model, "__compress_orderby__", None)
    valid_orderby = validate_compress_orderby_field(model, compress_orderby)
    compress_segmentby = getattr(model, "__compress_segmentby__", None)
    valid_segmentby = validate_compress_segmentby_field(model, compress_segmentby)
    validate_unique_segmentby_and_orderby_fields(
        model, compress_segmentby, compress_orderby
    )
    params = {}
    has_orderby = valid_orderby and compress_orderby is not None
    has_segmentby = valid_segmentby and compress_segmentby is not None
    if has_orderby:
        params["compress_orderby"] = compress_orderby
    if has_segmentby:
        params["compress_segmentby"] = compress_segmentby

    sql_template = sql.get_alter_compression_policy_sql(
        model.__tablename__, with_orderby=has_orderby, with_segmentby=has_segmentby
    )

    query = sqlalchemy.text(sql_template).bindparams(**params)
    compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))
    session.execute(sqlalchemy.text(compiled_query))
    if commit:
        session.commit()
