from typing import Any, Dict, List

from sqlalchemy import Float, Numeric, text
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlmodel import Session, func, select

from timescaledb.hyperfunctions import time_bucket, time_bucket_gapfill


def time_bucket_query(
    session: Session,
    model: Any,
    interval: str = "1 hour",
    time_field: str = "time",
    metric_field: str = "metric",
    decimal_places: int = 4,
    round_to_nearest: bool = True,
    annotations: Dict = None,
) -> List[Dict]:
    """
    SQLModel implementation of TimescaleDB time_bucket function.

    Args:
        session: SQLModel session
        model: The SQLModel class to query
        interval: Time interval (e.g., '1 hour', '1 day')
        field: The timestamp field to bucket (defaults to 'time')
        metric: The metric field to aggregate (defaults to 'metric')
    """
    if isinstance(time_field, InstrumentedAttribute):
        time_field = time_field.key
    if isinstance(metric_field, InstrumentedAttribute):
        metric_field = metric_field.key
    model_timescale_field_value = getattr(model, time_field)
    metric_field_value = getattr(model, metric_field)
    bucket = time_bucket(interval, model_timescale_field_value)
    avg_func = func.avg(metric_field_value)
    if round_to_nearest:
        avg_func = func.cast(
            func.round(func.cast(avg_func, Numeric), decimal_places),
            Float,
        )
    query = (
        select(
            bucket.label("bucket"),
            avg_func.label("avg"),
        )
        .group_by(bucket)
        .order_by(bucket.desc())
    )

    result = session.exec(query)
    result = result.mappings().all()
    return list(result)


def time_bucket_gapfill_query(
    session: Session,
    model: Any,
    interval: str = "1 hour",
    time_field: str = "time",
    metric_field: str = "metric",
    start: Any = None,
    finish: Any = None,
    use_interpolate: bool = False,
    use_locf: bool = False,
    bucket_label: str = "bucket",
    value_label: str = "avg",
) -> List[Dict]:
    if isinstance(time_field, InstrumentedAttribute):
        time_field = time_field.key
    if isinstance(metric_field, InstrumentedAttribute):
        metric_field = metric_field.key

    model_timescale_field_value = getattr(model, time_field)
    metric_field_value = getattr(model, metric_field)

    # Remove any timezone info from start/finish if present
    if start and start.tzinfo:
        start = start.replace(tzinfo=None)
    if finish and finish.tzinfo:
        finish = finish.replace(tzinfo=None)

    # Create the gapfill bucket
    bucket = time_bucket_gapfill(
        interval,
        model_timescale_field_value,
        start=start,
        finish=finish,
    )

    # Build the query with window functions for gapfilling
    avg_func = func.avg(metric_field_value)

    # Apply gapfilling strategy
    if use_locf:
        data_func = func.locf(avg_func)
    elif use_interpolate:
        data_func = func.interpolate(avg_func)
    else:
        data_func = avg_func

    query = (
        select(
            bucket.label(bucket_label),
            data_func.label(value_label),
        )
        .filter(model_timescale_field_value >= start)
        .filter(model_timescale_field_value <= finish)
        .group_by(bucket)
        .order_by(text(f"{bucket_label} ASC"))
    )
    result = session.exec(query)
    result = result.mappings().all()
    return list(result)
