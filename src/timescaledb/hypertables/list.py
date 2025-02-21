from typing import List

import sqlalchemy
from sqlmodel import Session

from timescaledb.hypertables import sql_statements as sql
from timescaledb.hypertables.schemas import HyperTableSchema


def list_hypertables(session: Session) -> List[HyperTableSchema]:
    """
    List all hypertables in the database

    Returns:
        List[HyperTableSchema]: A list of HyperTableSchema objects containing hypertable information
    """
    rows = session.execute(
        sqlalchemy.text(sql.LIST_AVAILABLE_HYPERTABLES_SQL)
    ).fetchall()
    return [HyperTableSchema(**dict(row._mapping)) for row in rows]