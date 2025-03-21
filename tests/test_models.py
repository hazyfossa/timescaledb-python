from datetime import datetime, timedelta

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlmodel import Session

# from timescaledb.defaults import TIME_COLUMN
# from timescaledb.engine import create_engine
import timescaledb
from timescaledb.compression.add import add_compression_policy
from timescaledb.hypertables.schemas import HyperTableSchema

from .conftest import (
    Metric,
    Record,
    VideoView,
    test_hypertables_list,
)


def test_model_table_exists(session: Session, engine: Engine):
    """Test that the model table exists."""
    inspector = inspect(engine)
    available_tables = inspector.get_table_names()
    assert len(available_tables) in range(7, 15)
    assert Metric.__tablename__ in available_tables, "Metrics table was not created!"
    assert Record.__tablename__ in available_tables, "Record table was not created!"
    assert VideoView.__tablename__ in available_tables, "View table was not created!"


def test_timescale_model_data_insert(session: Session, engine: Engine):
    """Test that TimescaleModel-based tables can be created and used."""

    # Create a test metric with explicit UTC timezone
    metric = Metric(
        sensor_id=1,
        value=23.5,
    )
    session.add(metric)
    session.commit()
    session.refresh(metric)
    assert metric.id is not None, f"ID is None: {metric.id}"
    assert metric.time is not None, f"Time is None: {metric.time}"
    assert metric.sensor_id == 1, f"Sensor ID mismatch: {metric.sensor_id}"
    assert metric.value == 23.5, f"Value mismatch: {metric.value}"
    print("tz", metric.time.tzinfo)
    assert metric.time.tzinfo is not None, f"Time has no timezone: {metric.time}"
    assert (
        metric.time.tzinfo.tzname(None) == "UTC"
    ), f"Not UTC timezone: {metric.time.tzinfo}"


def test_hypertables(session: Session, engine: Engine):
    """Test that hypertables are created correctly."""
    hypertables = timescaledb.list_hypertables(session)
    # automatic hypertables + 1 for manual hypertable
    assert len(hypertables) in [
        len(test_hypertables_list),
        len(test_hypertables_list) + 1,
    ]
    first_item = hypertables[0]
    assert isinstance(first_item, HyperTableSchema)
    assert first_item.hypertable_name == Metric.__tablename__


def test_time_bucket_query(session: Session):
    """Test the time_bucket_query function."""
    # Create test data
    metrics = [
        Metric(sensor_id=1, value=20.0),
        Metric(sensor_id=1, value=22.0),
        Metric(sensor_id=1, value=24.0),
        Metric(sensor_id=1, value=26.0),
    ]
    session.add_all(metrics)
    session.commit()

    # Query with 1 day interval
    results = timescaledb.queries.time_bucket_query(
        session,
        Metric,
        interval="1 day",
        time_field="time",
        metric_field="value",
        decimal_places=2,
    )

    assert len(results) == 1, "Expected one bucket for same-day measurements"
    assert "bucket" in results[0], "Missing bucket field in result"
    assert "avg" in results[0], "Missing avg field in result"
    assert (
        results[0]["avg"] == 23.0
    ), f"Expected average of 23.0, got {results[0]['avg']}"


def test_time_bucket_gapfill_query(session: Session):
    """Test the time_bucket_gapfill_query function."""
    from datetime import datetime, timedelta

    # Create test data with a gap
    base_time = datetime(2024, 1, 1, 12, 0)
    metrics = [
        Metric(sensor_id=1, value=20.0, time=base_time),
        Metric(sensor_id=1, value=22.0, time=base_time + timedelta(hours=1)),
        # Gap of 2 hours
        Metric(sensor_id=1, value=24.0, time=base_time + timedelta(hours=4)),
        Metric(sensor_id=1, value=26.0, time=base_time + timedelta(hours=5)),
    ]
    session.add_all(metrics)
    session.commit()

    # Query with 1-hour intervals and gapfill
    results = timescaledb.queries.time_bucket_gapfill_query(
        session,
        Metric,
        interval="1 hour",
        time_field="time",
        metric_field="value",
        start=base_time,
        finish=base_time + timedelta(hours=5),
        use_interpolate=True,
    )

    assert len(results) == 6, "Expected 6 hourly buckets"

    # First bucket should have data
    assert results[0]["avg"] is not None, "First bucket should have data"

    # Middle buckets should be interpolated
    assert all(
        r["avg"] is not None for r in results
    ), "All buckets should have values when interpolating"

    # Test with LOCF (Last Observation Carried Forward)
    results_locf = timescaledb.queries.time_bucket_gapfill_query(
        session,
        Metric,
        interval="1 hour",
        time_field="time",
        metric_field="value",
        start=base_time,
        finish=base_time + timedelta(hours=5),
        use_locf=True,
    )

    assert len(results_locf) == 6, "Expected 6 hourly buckets with LOCF"
    assert all(
        r["avg"] is not None for r in results_locf
    ), "All buckets should have values when using LOCF"


def test_time_bucket_query_invalid_params(session: Session):
    """Test time_bucket_query with invalid parameters."""
    # Test with invalid metric field
    with pytest.raises(ValueError, match="Column .* not found"):
        timescaledb.queries.time_bucket_query(
            session,
            Metric,
            interval="1 day",
            time_field="time",
            metric_field="nonexistent_field",
        )

    # Test with invalid time field
    with pytest.raises(ValueError, match="Column .* not found"):
        timescaledb.queries.time_bucket_query(
            session,
            Metric,
            interval="1 day",
            time_field="nonexistent_time",
            metric_field="value",
        )


def test_time_bucket_gapfill_query_invalid_params(session: Session):
    """Test time_bucket_gapfill_query with invalid parameters."""

    base_time = datetime(2024, 1, 1, 12, 0)

    # Test with invalid metric field
    with pytest.raises(ValueError, match="Column .* not found"):
        timescaledb.queries.time_bucket_gapfill_query(
            session,
            Metric,
            interval="1 hour",
            time_field="time",
            metric_field="nonexistent_field",
            start=base_time,
            finish=base_time + timedelta(hours=5),
        )

    # Test with invalid time field
    with pytest.raises(ValueError, match="Column .* not found"):
        timescaledb.queries.time_bucket_gapfill_query(
            session,
            Metric,
            interval="1 hour",
            time_field="nonexistent_time",
            metric_field="value",
            start=base_time,
            finish=base_time + timedelta(hours=5),
        )

    # Test with finish time before start time
    with pytest.raises(ValueError, match="Finish time must be after start time"):
        timescaledb.queries.time_bucket_gapfill_query(
            session,
            Metric,
            interval="1 hour",
            time_field="time",
            metric_field="value",
            start=base_time,
            finish=base_time - timedelta(hours=1),
        )


def test_time_bucket_query_with_filters(session: Session):
    """Test time_bucket_query with additional filters."""
    # Create test data with different sensor IDs
    metrics = [
        Metric(sensor_id=1, value=20.0),
        Metric(sensor_id=1, value=22.0),
        Metric(sensor_id=2, value=24.0),
        Metric(sensor_id=2, value=26.0),
    ]
    session.add_all(metrics)
    session.commit()

    # Query with filter for sensor_id=1
    results = timescaledb.queries.time_bucket_query(
        session,
        Metric,
        interval="1 day",
        time_field="time",
        metric_field="value",
        filters=[Metric.sensor_id == 1],
    )

    assert len(results) == 1, "Expected one bucket for filtered measurements"
    assert (
        results[0]["avg"] == 21.0
    ), f"Expected average of 21.0, got {results[0]['avg']}"


def test_time_bucket_gapfill_query_with_filters(session: Session):
    """Test time_bucket_gapfill_query with additional filters."""

    base_time = datetime(2024, 1, 1, 12, 0)
    metrics = [
        Metric(sensor_id=1, value=20.0, time=base_time),
        Metric(sensor_id=1, value=22.0, time=base_time + timedelta(hours=1)),
        Metric(sensor_id=2, value=24.0, time=base_time + timedelta(hours=2)),
        Metric(sensor_id=2, value=26.0, time=base_time + timedelta(hours=3)),
    ]
    session.add_all(metrics)
    session.commit()

    # Query with filter for sensor_id=1 and LOCF (Last Observation Carried Forward)
    results = timescaledb.queries.time_bucket_gapfill_query(
        session,
        Metric,
        interval="1 hour",
        time_field="time",
        metric_field="value",
        start=base_time,
        finish=base_time + timedelta(hours=4),
        filters=[Metric.sensor_id == 1],
        use_locf=True,
    )

    assert len(results) == 4, "Expected 4 hourly buckets"
    assert results[0]["avg"] == 20.0, "First bucket should match first measurement"
    assert results[1]["avg"] == 22.0, "Second bucket should match second measurement"
    # The remaining buckets should use the last known value (22.0)
    assert results[2]["avg"] == 22.0, "Third bucket should use last known value"
    assert results[3]["avg"] == 22.0, "Fourth bucket should use last known value"

    # Test without gap filling
    results_no_fill = timescaledb.queries.time_bucket_gapfill_query(
        session,
        Metric,
        interval="1 hour",
        time_field="time",
        metric_field="value",
        start=base_time,
        finish=base_time + timedelta(hours=4),
        filters=[Metric.sensor_id == 1],
    )

    assert len(results_no_fill) == 4, "Expected 4 hourly buckets"
    assert results_no_fill[0]["avg"] == 20.0, "First bucket should have data"
    assert results_no_fill[1]["avg"] == 22.0, "Second bucket should have data"
    assert results_no_fill[2]["avg"] is None, "Third bucket should be NULL"
    assert results_no_fill[3]["avg"] is None, "Fourth bucket should be NULL"


def test_add_compression_policy(session: Session):
    """Test that the compression policy is created correctly."""
    add_compression_policy(session, VideoView)
