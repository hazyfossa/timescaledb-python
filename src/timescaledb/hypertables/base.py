from typing import List, Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.hypertables import sql_statements as sql
from timescaledb.hypertables import validators
from timescaledb.hypertables.schemas import HyperTableSchema
from timescaledb.models import TimescaleModel


def create_hypertable(
    session: Session,
    model: Type[SQLModel],
    if_not_exists: bool = True,
    migrate_data: bool = True,
    commit: bool = True,
) -> None:
    """
    Create a hypertable from a SQLModel class
    """
    time_field = model.__time_column__
    validators.validate_time_column(model, time_field)
    time_interval = model.__chunk_time_interval__
    validators.validate_time_interval(model, time_interval)

    table_name = model.__tablename__
    params = {
        "table_name": table_name,
        "time_field": time_field,
        "time_interval": time_interval,
        "if_not_exists": str(if_not_exists).lower(),
        "migrate_data": str(migrate_data).lower(),
    }
    # session.execute(sqlalchemy.text(sql.CREATE_HYPERTABLE_SQL), params)

    CREATE_HYPERTABLE_SQL = """SELECT create_hypertable(
            '{table_name}', 
            by_range('{time_field}', INTERVAL '{time_interval}'),
            if_not_exists => '{if_not_exists}',
            migrate_data => '{migrate_data}'
        );
    """.format(**params)
    session.execute(sqlalchemy.text(CREATE_HYPERTABLE_SQL))
    if commit:
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
        create_hypertable(session, model, if_not_exists=True, migrate_data=True)


def list_hypertables(session: Session) -> List[HyperTableSchema]:
    """
    List all hypertables in the database

    Returns:
        List[dict]: A list of dictionaries containing hypertable information
    """
    rows = session.execute(sqlalchemy.text(sql.LIST_HYPERTABLES_SQL)).fetchall()
    return [HyperTableSchema(**dict(row._mapping)) for row in rows]
