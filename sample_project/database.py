from sqlmodel import Session, SQLModel

import timescaledb

from .config import (
    DATABASE_URL,
    ECHO_QUERIES,
    TIME_ZONE,
)

# time zone focused wrapper for sqlmodel.create_engine/sqlalchemy.create_engine
engine = timescaledb.create_engine(DATABASE_URL, timezone=TIME_ZONE, echo=ECHO_QUERIES)


def init_db():
    # Create all tables
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)

    print("Creating hypertables...")
    timescaledb.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
