from typing import Type

from sqlmodel import Session, SQLModel

from timescaledb.hypertables.create import create_hypertable
from timescaledb.models import TimescaleModel


def sync_all_hypertables(session: Session, *models: Type[SQLModel]) -> None:
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
        create_hypertable(
            session,
            commit=False,
            model=model,
            table_name=None,
            hypertable_options={
                "if_not_exists": True,
                "migrate_data": True,
            },
        )
    session.commit()
