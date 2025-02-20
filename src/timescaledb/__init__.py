from __future__ import annotations

__version__ = "0.0.2"

from . import metadata
from .activator import activate_timescaledb_extension
from .engine import create_engine
from .hypertables import (
    create_hypertable,
    list_hypertables,
    sync_all_hypertables,
)
from .models import TimescaleModel
from .queries import time_bucket_gapfill_query, time_bucket_query

__all__ = [
    "metadata",
    "TimescaleModel",
    "activate_timescaledb_extension",
    "sync_all_hypertables",
    "create_hypertable",
    "list_hypertables",
    "create_engine",
    "time_bucket_query",
    "time_bucket_gapfill_query",
    "defaults",
    "get_defaults",
]
