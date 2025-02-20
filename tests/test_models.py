from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, select

# from timescaledb.defaults import TIME_COLUMN
# from timescaledb.engine import create_engine
import timescaledb
from timescaledb.hypertables.schemas import HyperTableSchema
from timescaledb.models import TimescaleModel


class Record(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str


class Metric(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    sensor_id: int = Field(index=True)
    value: float

    # Enable compression for testing
    __enable_compression__ = False


@pytest.fixture(scope="function", autouse=True)
def migrate_database(engine: Engine):
    """Migrate the database to the latest version."""
    print("Starting database migration...")  # Debug print
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    timescaledb.metadata.create_all(engine)
    return engine


def test_model_table_exists(session: Session, engine: Engine):
    """Test that the model table exists."""
    inspector = inspect(engine)
    available_tables = inspector.get_table_names()
    assert len(available_tables) == 2
    assert Metric.__tablename__ in available_tables, "Metrics table was not created!"
    assert Record.__tablename__ in available_tables, "Record table was not created!"


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
    assert len(hypertables) == 1
    first_item = hypertables[0]
    assert isinstance(first_item, HyperTableSchema)
    assert first_item.hypertable_name == Metric.__tablename__
