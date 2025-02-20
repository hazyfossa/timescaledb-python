from typing import List

import sqlalchemy
from sqlmodel import Session

from timescaledb.hypertables.chunks import sql_statements as sql


def show_chunks(
    session: Session, table_name: str, *, condition: str = None
) -> List[any]:
    """
    Show chunks for a table with a condition
    """
    if condition:
        query = sqlalchemy.text(sql.SHOW_CHUNKS_CONDITIONAL_SQL).bindparams(
            **{"table_name": table_name, "condition": condition}
        )
        compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))
    else:
        query = sql.SHOW_CHUNKS.bindparams(**{"table_name": table_name})
        compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))
    return session.execute(sqlalchemy.text(compiled_query)).fetchall()
