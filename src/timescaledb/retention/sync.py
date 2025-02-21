from typing import Type

from sqlmodel import Session, SQLModel

from timescaledb.models import TimescaleModel
from timescaledb.retention.add import add_retention_policy


def sync_retention_policies(
    session: Session, *models: Type[SQLModel], drop_after=None
) -> None:
    """
    Enable compression for all hypertables
    """
    if models:
        model_list = models
    else:
        model_list = [
            model
            for model in TimescaleModel.__subclasses__()
            if getattr(model, "__table__", None) is not None
        ]
    for model in model_list:
        add_retention_policy(session, model, commit=False, drop_after=drop_after)
    session.commit()
