from typing import List, Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.hypertables import sql_statements as sql
from timescaledb.hypertables import validators
from timescaledb.models import TimescaleModel


def enable_compression(session: Session, model: Type[SQLModel]) -> None:
    """
    Enable compression for a hypertable
    """
    enable_compression = model.__enable_compression__
    if not enable_compression:
        return

    # Validate all required compression parameters are present
    if model.__compress_after__ is None:
        raise ValueError(
            f"Missing required compression parameter: __compress_after__ for model {model.__name__}"
        )

    # Build compression parameters dict with optional parameters
    compression_params = {
        "table_name": model.__tablename__,
        "compress_after": model.__compress_after__,
    }

    # Add optional parameters if they are set
    if model.__compress_segmentby__ is not None:
        compression_params["segmentby"] = model.__compress_segmentby__
        # Validate segmentby field if provided
        validators.validate_compress_segmentby_field(
            model, model.__compress_segmentby__
        )

    if model.__compress_orderby__ is not None:
        compression_params["compress_orderby"] = model.__compress_orderby__
        # Validate orderby field if provided
        validators.validate_compress_orderby_field(model, model.__compress_orderby__)

    if model.__drop_after__ is not None:
        compression_params["compress_drop_after"] = model.__drop_after__

    # Use the SQL statement from sql_statements.py
    session.execute(
        sqlalchemy.text(sql.ENABLE_COMPRESSION_SQL),
        compression_params,
    )
    session.commit()


def enable_compression_for_all_hypertables(
    session: Session, *models: Type[SQLModel]
) -> None:
    """
    Enable compression for all hypertables
    """
    if models:
        model_list = models
    else:
        model_list = [
            model
            for model in TimescaleModel.__subclasses__()
            if getattr(model, "__table__", None) is not None
        ]
    for model in model_list:
        enable_compression(session, model)
        compress_enabled = model.__enable_compression__
        if not compress_enabled:
            continue
