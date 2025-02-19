from typing import List, Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.models import TimescaleModel
from timescaledb.validators import validate_time_field


def activate_timescaledb_extension(session: Session) -> None:
    session.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
    session.commit()


def create_hypertable(
    session: Session,
    model: Type[SQLModel],
    if_not_exists: bool = True,
    migrate_data: bool = True,
) -> None:
    """
    Create a hypertable from a SQLModel class
    """
    time_field = model.__timescale_field__
    time_interval = model.__timescale_time_interval__ or "7 days"
    if time_field is None:
        raise ValueError(f"Model {model.__name__} does not specify __timescale_field__")
    table_name = model.__tablename__

    # SQL command to create hypertable
    create_hypertable_sql = f"""
    SELECT create_hypertable(
        '{table_name}', 
        by_range('{time_field}', INTERVAL '{time_interval}'),
        if_not_exists => {str(if_not_exists).lower()},
        migrate_data => {str(migrate_data).lower()}
    );
    """
    session.execute(sqlalchemy.text(create_hypertable_sql))
    session.commit()


def create_all_hypertables(session: Session, *models: Type[SQLModel]) -> None:
    """
    Set up hypertables for all models that inherit from TimescaleModel.
    If no models are provided, all SQLModel subclasses in the current SQLModel registry will be checked.

    Args:
        session: SQLModel session
        *models: Optional specific models to set up. If none provided, all models will be checked.
    """
    if models:
        model_list = models
    else:
        # Get all TimescaleModel subclasses that have table=True
        model_list = [
            model
            for model in TimescaleModel.__subclasses__()
            if getattr(model, "__table__", None) is not None
        ]
    for model in model_list:
        # Get the time field name from the class variable
        time_field_name = model.__timescale_field__
        if time_field_name is None:
            raise ValueError(
                f"Model {model.__name__} does not specify __timescale_field__"
            )
        if not validate_time_field(model, time_field_name):
            raise ValueError(f"Model {model.__name__} is missing a valid timefield")

        create_hypertable(session, model, if_not_exists=True, migrate_data=True)


def list_hypertables(session: Session) -> List[dict]:
    """
    List all hypertables in the database

    Returns:
        List[dict]: A list of dictionaries containing hypertable information
    """
    rows = session.execute(
        sqlalchemy.text("SELECT * FROM timescaledb_information.hypertables")
    ).fetchall()
    return [dict(row._mapping) for row in rows]
