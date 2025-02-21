from sqlmodel import Session

from timescaledb import create_hypertable

from .conftest import ManualHypertable


def test_manual_hypertable(session: Session):
    tablename = ManualHypertable.__tablename__
    hypertable_options = {
        "time_column": "time",
        "chunk_time_interval": "1 day",
    }
    create_hypertable(
        session,
        table_name=tablename,
        hypertable_options=hypertable_options,
        commit=True,
    )
