from typing import Type

import sqlalchemy
from sqlmodel import SQLModel


def validate_time_field(model: Type[SQLModel], timescale_field: str = "time") -> bool:
    """
    Verify if the specified field is a valid time field (DateTime or TIMESTAMP)
    """
    # Get the column type from SQLModel
    column = model.__table__.columns.get(timescale_field)
    if column is None:
        return False

    # Check if the column type is DateTime or TIMESTAMP
    column_type = type(column.type)
    is_valid = column_type in (sqlalchemy.DateTime, sqlalchemy.TIMESTAMP)
    return is_valid
