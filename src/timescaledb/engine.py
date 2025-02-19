from sqlalchemy import create_engine as create_engine_sqlalchemy


def create_engine(url: str, timezone: str = "UTC", *args, **kwargs):
    """
    Create a SQLAlchemy create_engine wrapper
    that ensures that the timezone is set for the timestamp columns.

    Args:
        url: Database URL
        timezone: Timezone for timestamp columns
    """

    connect_args = kwargs.get("connect_args", {})
    connect_args["options"] = f"-c timezone={timezone}"
    return create_engine_sqlalchemy(url, connect_args=connect_args, *args, **kwargs)
