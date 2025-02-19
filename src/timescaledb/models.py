from datetime import datetime, timezone
from typing import Optional

# from sqlalchemy import TIMESTAMP
from sqlmodel import Field, SQLModel


class TimescaleModel(SQLModel):
    """Base class for Timescale hypertables"""

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    time: datetime = Field(
        default_factory=lambda: datetime.utcnow().replace(tzinfo=timezone.utc),
        index=True,
        primary_key=True,
    )
    # Class variable to specify the timestamp field
    __timescale_field__ = "time"
    __timescale_time_interval__ = "7 days"
