from datetime import datetime
from typing import Optional

import sqlmodel
from sqlmodel import Field, SQLModel

from timescaledb.defaults import (
    CHUNK_TIME_INTERVAL,
    COMPRESS_AFTER,
    COMPRESS_ORDERBY,
    COMPRESS_SEGMENTBY,
    DROP_AFTER,
    TIME_COLUMN,
)
from timescaledb.utils import get_utc_now


class TimescaleModel(SQLModel):
    """Base class for Timescale hypertables"""

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    time: datetime = Field(
        default_factory=get_utc_now,
        sa_column=sqlmodel.Column(
            sqlmodel.DateTime(timezone=True),
            index=True,
            primary_key=True,
            nullable=False,
        ),
    )
    # Class variable to specify the TimescaleDB time field
    __time_column__ = TIME_COLUMN
    # Class variable to specify the TimescaleDB chunk time interval
    __chunk_time_interval__ = CHUNK_TIME_INTERVAL

    # Class variables to specify TimescaleDB compression settings
    __enable_compression__ = False
    # Class variable to specify the TimescaleDB compression segmentby
    __compress_segmentby__ = COMPRESS_SEGMENTBY
    # Class variable to specify the TimescaleDB compression after
    __compress_after__ = COMPRESS_AFTER
    # Class variable to specify the TimescaleDB compression orderby
    __compress_orderby__ = COMPRESS_ORDERBY
    # Class variable to specify the TimescaleDB compression drop after
    __drop_after__ = DROP_AFTER
