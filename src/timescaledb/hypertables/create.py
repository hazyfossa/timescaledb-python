from datetime import timedelta
from typing import Type

import sqlalchemy
from sqlmodel import Session, SQLModel

from timescaledb.hypertables import sql_statements as sql
from timescaledb.hypertables import validators

HYPERTABLE_INTERVAL_TYPE_SQL = {
    "INTERVAL": sql.CREATE_HYPERTABLE_SQL_VIA_INTERVAL,
    "TIMESTAMP": sql.CREATE_HYPERTABLE_SQL_VIA_TIMESTAMP,
}


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
    time_column = getattr(model, "__time_column__", None)
    validators.validate_time_column(model, time_column)
    interval = getattr(model, "__chunk_time_interval__", None)
    validators.validate_chunk_time_interval(model, time_column, interval)
    sql_template = None
    cleaned_interval = None
    if isinstance(interval, timedelta):
        # Convert to microseconds
        cleaned_interval = int(interval.total_seconds())
        sql_template = HYPERTABLE_INTERVAL_TYPE_SQL["TIMESTAMP"]
    elif isinstance(interval, int):
        # Microseconds
        cleaned_interval = interval
        sql_template = HYPERTABLE_INTERVAL_TYPE_SQL["TIMESTAMP"]
    elif isinstance(interval, str):
        # Such as INTERVAL 1 day
        # or INTERVAL '2 weeks'
        # pop the term "INTERVAL"
        cleaned_interval = interval.replace("INTERVAL", "").strip()
        # remove any extra quotes
        cleaned_interval = cleaned_interval.replace("'", "").replace('"', "")
        sql_template = HYPERTABLE_INTERVAL_TYPE_SQL["INTERVAL"]
    else:
        raise ValueError("Invalid interval type")
    if sql_template is None or cleaned_interval is None:
        raise ValueError("Invalid interval type")

    table_name = getattr(model, "__tablename__", None)
    params = {
        "table_name": table_name,
        "time_column": time_column,
        "chunk_time_interval": cleaned_interval,
        "if_not_exists": "true" if if_not_exists else "false",
        "migrate_data": "true" if migrate_data else "false",
    }
    query = sqlalchemy.text(sql_template).bindparams(**params)
    compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))
    session.execute(sqlalchemy.text(compiled_query))
    if commit:
        session.commit()
