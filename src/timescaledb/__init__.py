from __future__ import annotations

__version__ = "0.0.2"

from . import metadata
from .engine import create_engine
from .models import TimescaleModel
from .queries import time_bucket_gapfill_query, time_bucket_query
from .utils import (
    activate_timescaledb_extension,
    create_all_hypertables,
    create_hypertable,
    list_hypertables,
)

__all__ = [
    "metadata",
    "TimescaleModel",
    "activate_timescaledb_extension",
    "create_all_hypertables",
    "create_hypertable",
    "list_hypertables",
    "create_engine",
    "time_bucket_query",
    "time_bucket_gapfill_query",
]
