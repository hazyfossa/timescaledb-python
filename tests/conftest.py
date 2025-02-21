from datetime import datetime, timedelta
from typing import Generator, Optional

import pytest
import sqlmodel
from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel
from testcontainers.postgres import PostgresContainer

import timescaledb
from timescaledb.engine import create_engine
from timescaledb.models import TimescaleModel
from timescaledb.utils import get_utc_now


@pytest.fixture(scope="session", autouse=True)
def timescale_container() -> Generator[PostgresContainer, None, None]:
    """Creates a TimescaleDB test container that can be used across multiple tests."""
    timescale_db = PostgresContainer(
        image="timescale/timescaledb:latest-pg17",
        username="test_user",
        password="test_password",
        dbname="test_db",
    )
    with timescale_db as container:
        container.start()
        yield container


@pytest.fixture(name="engine")
def engine_fixture(timescale_url: str):
    """Create a fresh database for each test."""
    engine = create_engine(timescale_url, timezone="UTC", echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new database session for each test."""
    session = Session(engine)
    yield session
    session.close()


@pytest.fixture(scope="session")
def timescale_url(timescale_container: PostgresContainer) -> str:
    """Get the database URL using the container's dynamic port."""
    host = timescale_container.get_container_host_ip()
    port = timescale_container.get_exposed_port(timescale_container.port)
    db_name = timescale_container.dbname
    user = timescale_container.username
    password = timescale_container.password
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"


class Record(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str


class ManualHypertable(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
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


class Metric(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    sensor_id: int = Field(index=True)
    value: float

    __table_name__ = "metrics"
    __enable_compression__ = False


class VideoView(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    duration: int
    video_id: int = Field(index=True)

    __table_name__ = "video_views"
    __enable_compression__ = True
    __compress_chunk_time_interval__ = "INTERVAL 1 day"
    __compress_orderby__ = "time DESC"
    __compress_segmentby__ = "video_id"


class PageView(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    path: str = Field(index=True)

    __table_name__ = "page_views"
    __enable_compression__ = True
    __chunk_time_interval__ = timedelta(days=30)
    __compress_orderby__ = "time ASC"
    __compress_segmentby__ = "path"


class SimpleCompression(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    value: int

    __table_name__ = "simple_compression"
    __enable_compression__ = True


class SimpleCompressionWithOrderby(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    value: int

    __table_name__ = "simple_compression_with_orderby"
    __enable_compression__ = True
    __compress_orderby__ = "value ASC"


class SimpleCompressionWithSegmentby(TimescaleModel, table=True):
    """Test model for TimescaleDB functionality."""

    value: int

    __table_name__ = "simple_compression_with_segmentby"
    __enable_compression__ = True
    __compress_segmentby__ = "value"


@pytest.fixture(scope="function", autouse=True)
def migrate_database(engine: Engine):
    """Migrate the database to the latest version."""
    print("Starting database migration...")  # Debug print
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    timescaledb.metadata.create_all(engine)
    return engine


test_hypertables_list = [
    Metric,
    VideoView,
    PageView,
    SimpleCompression,
    SimpleCompressionWithOrderby,
    SimpleCompressionWithSegmentby,
]
test_regular_tables_list = [Record]
