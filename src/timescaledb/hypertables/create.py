from typing import Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.hypertables import sql_statements as sql
from timescaledb.hypertables import validators


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
        "if_not_exists": "true" if if_not_exists else "false",
        "migrate_data": "true" if migrate_data else "false",
    }
    query = sqlalchemy.text(sql.CREATE_HYPERTABLE_SQL).bindparams(**params)
    compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))
    session.execute(sqlalchemy.text(compiled_query))
    if commit:
        session.commit()
