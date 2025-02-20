import os
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel
from testcontainers.postgres import PostgresContainer

from timescaledb.engine import create_engine


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
