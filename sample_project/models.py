from datetime import datetime, timezone

from pydantic import validator
from sqlmodel import Field, SQLModel

from timescaledb import TimescaleModel


class Metric(TimescaleModel, table=True):
    temp: float = Field(index=True)


class MetricCreate(SQLModel):
    temp: float


class MetricRead(SQLModel):
    id: int
    temp: float
    time: datetime = Field(default=None)

    @validator("time")
    def ensure_timezone(cls, v):
        if v and v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v


# Hypertables = [Metric]
