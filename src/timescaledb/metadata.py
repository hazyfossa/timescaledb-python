from sqlalchemy.engine import Engine
from sqlmodel import Session

from timescaledb.utils import activate_timescaledb_extension, create_all_hypertables


def create_all(engine: Engine) -> None:
    with Session(engine) as session:
        activate_timescaledb_extension(session)
        create_all_hypertables(session)
