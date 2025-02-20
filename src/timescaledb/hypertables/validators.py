from typing import Type

import sqlalchemy
from sqlmodel import SQLModel

from timescaledb import exceptions


def validate_time_column(model: Type[SQLModel], time_column: str = "time") -> bool:
    """
    Verify if the specified field is a valid time field (DateTime or TIMESTAMP)
    """
    # Get the column type from SQLModel
    column = model.__table__.columns.get(time_column)
    if column is None:
        raise exceptions.InvalidTimeColumn(
            f"Model {model.__name__} does not have a valid time column"
        )

    # Check if the column type is DateTime or TIMESTAMP
    column_type = type(column.type)
    is_valid = column_type in (
        sqlalchemy.DateTime,
        sqlalchemy.TIMESTAMP,
    )
    if not is_valid:
        raise exceptions.InvalidTimeColumnType(
            f"Model {model.__name__} has an invalid data type for the time column. "
            "Use sqlalchemy.DateTime or sqlalchemy.TIMESTAMP"
        )


def validate_time_interval(model: Type[SQLModel], time_interval: str) -> bool:
    """
    Verify if the specified time interval is a valid time interval
    1 <interval>
    N <interval>s

    <interval> is one of:
    - second
    - minute
    - hour
    - day
    - week
    - month

    Such as:

    1 day
    7 days
    """
    if time_interval is None:
        raise exceptions.TimeIntervalNotSet(
            f"Time interval is not set for model {model.__name__}"
        )
    valid_units = {
        "second": "seconds",
        "minute": "minutes",
        "hour": "hours",
        "day": "days",
        "week": "weeks",
        "month": "months",
        "year": "years",
    }
    try:
        # Split the interval string into number and unit
        parts = time_interval.strip().split()
        if len(parts) != 2:
            raise exceptions.InvalidTimeInterval(
                f"Invalid time interval format: {time_interval}. "
                "Expected format: '<number> <unit>'"
            )

        number, unit = parts

        # Validate the number part
        try:
            number = int(number)
            if number <= 0:
                raise ValueError
        except ValueError:
            raise exceptions.InvalidTimeInterval(
                f"Invalid time interval number: {number}. " "Must be a positive integer"
            )

        # Validate the unit part
        unit = unit.lower()
        if unit in valid_units:
            return True
        elif unit in valid_units.values():
            return True
        else:
            raise exceptions.InvalidTimeInterval(
                f"Invalid time interval unit: {unit}. "
                f"Must be one of: {', '.join(valid_units.keys())}"
            )

    except exceptions.InvalidTimeInterval:
        raise
    except Exception as e:
        raise exceptions.InvalidTimeInterval(
            f"Invalid time interval: {time_interval}. {str(e)}"
        )


def validate_compress_segmentby_field(
    model: Type[SQLModel], segmentby_field: str
) -> bool:
    """
    Verify if the specified field is a valid segmentby field.
    Valid types include String, Integer, Boolean, and other scalar types.
    Arrays and JSON types are not supported for segmentby.
    """
    column = model.__table__.columns.get(segmentby_field)
    if column is None:
        raise exceptions.InvalidSegmentByField(
            f"Field '{segmentby_field}' not found in model {model.__name__}"
        )

    # Types that are valid for segmentby
    valid_types = (
        sqlalchemy.String,
        sqlalchemy.Integer,
        sqlalchemy.SmallInteger,
        sqlalchemy.BigInteger,
        sqlalchemy.Boolean,
        sqlalchemy.Date,
        sqlalchemy.DateTime,
        sqlalchemy.Enum,
        sqlalchemy.Float,
        sqlalchemy.Numeric,
    )

    column_type = type(column.type)
    if not issubclass(column_type, valid_types):
        raise exceptions.InvalidSegmentByField(
            f"Field '{segmentby_field}' in model {model.__name__} has invalid type {column_type.__name__}. "
            f"Must be one of: {', '.join(t.__name__ for t in valid_types)}"
        )

    return True


def validate_compress_orderby_field(model: Type[SQLModel], orderby_field: str) -> bool:
    """
    Verify if the specified field is a valid orderby field.
    Most scalar types are valid for orderby, but they should be orderable.
    """
    column = model.__table__.columns.get(orderby_field)
    if column is None:
        raise exceptions.InvalidOrderByField(
            f"Field '{orderby_field}' not found in model {model.__name__}"
        )

    # Types that are not valid for orderby
    invalid_types = (
        sqlalchemy.JSON,
        sqlalchemy.ARRAY,
        sqlalchemy.PickleType,
    )

    column_type = type(column.type)
    if issubclass(column_type, invalid_types):
        raise exceptions.InvalidOrderByField(
            f"Field '{orderby_field}' in model {model.__name__} has invalid type {column_type.__name__}. "
            "JSON, ARRAY, and PickleType are not supported for orderby fields"
        )

    return True
