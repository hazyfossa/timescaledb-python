from sqlmodel import Session, SQLModel, create_engine

import timescaledb

from .config import DATABASE_URL, TIME_ZONE

engine = timescaledb.create_engine(DATABASE_URL, timezone=TIME_ZONE, echo=False)


def init_db():
    # Create all tables
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)

    print("Creating hypertables...")
    timescaledb.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
