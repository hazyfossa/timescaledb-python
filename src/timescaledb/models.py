from datetime import datetime
from typing import Optional

import sqlmodel
from sqlmodel import Field, SQLModel

from timescaledb.defaults import (
    CHUNK_TIME_INTERVAL,
    COMPRESS_ORDERBY,
    COMPRESS_SEGMENTBY,
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
        sa_type=sqlmodel.DateTime(timezone=True),
        primary_key=True,
        nullable=False,
    )
    # Class variable to specify the TimescaleDB time field
    __time_column__ = TIME_COLUMN
    # Class variable to specify the TimescaleDB chunk time interval
    __chunk_time_interval__ = CHUNK_TIME_INTERVAL

    # Class variables to specify TimescaleDB compression settings
    __enable_compression__ = False
    # Class variable to specify the TimescaleDB compression orderby
    __compress_orderby__ = COMPRESS_ORDERBY
    # Class variable to specify the TimescaleDB compression segmentby
    __compress_segmentby__ = COMPRESS_SEGMENTBY
    # Class variable to specify the TimescaleDB compression chunk time interval
    __compress_chunk_time_interval__ = None
