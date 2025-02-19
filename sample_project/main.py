from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, desc, func, select, text

from timescaledb import list_hypertables
from timescaledb.queries import time_bucket_gapfill_query

# from timescaledb.hyperfunctions import time_bucket
# from timescaledb.queries import get_histogram
from . import models
from .database import get_session, init_db

app = FastAPI(title="FastAPI SQLModel Demo")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root(session: Session = Depends(get_session)):
    hypertables = list_hypertables(session)
    return {"message": "Hello World", "hypertables": hypertables}


@app.post("/metrics/", response_model=models.MetricRead)
def create_metric(metric: models.MetricCreate, session: Session = Depends(get_session)):
    db_metric = models.Metric.from_orm(metric)
    session.add(db_metric)
    session.commit()
    session.refresh(db_metric)
    return db_metric


@app.get("/metrics/{metric_id}", response_model=models.MetricRead)
def read_metric(metric_id: int, session: Session = Depends(get_session)):
    metric = session.get(models.Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, message="Metric not found")
    return metric


@app.get("/metrics/", response_model=list[models.MetricRead])
def list_metrics(session: Session = Depends(get_session)):
    metrics = session.query(models.Metric).all()
    return metrics


@app.get("/users/{user_id}/metrics/", response_model=list[models.MetricRead])
def list_user_metrics(user_id: int, session: Session = Depends(get_session)):
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, message="User not found")
    metrics = (
        session.query(models.Metric).filter(models.Metric.user_id == user_id).all()
    )
    return metrics


@app.get("/metrics/buckets/", response_model=list[dict])
def get_metric_buckets(
    interval: str = "1 hour", session: Session = Depends(get_session)
):
    """Get metrics aggregated into time buckets"""
    latest_metric = (
        session.query(models.Metric).order_by(desc(models.Metric.time)).first()
    )

    if not latest_metric:
        return []
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)
    raw_results = time_bucket_gapfill_query(
        session=session,
        model=models.Metric,
        time_field="time",
        metric_field="temp",
        interval=interval,
        use_interpolate=True,
        use_locf=False,  # Disable LOCF to ensure we're using pure interpolation
        start=start_time,
        finish=end_time,
    )
    return raw_results


# @app.get("/metrics/histogram/", response_model=list[dict])
# def get_metric_histogram(
#     min_value: float,
#     max_value: float,
#     num_buckets: int = 5,
#     session: Session = Depends(get_session),
# ):
#     """Get histogram of metric temperatures"""
#     return get_histogram(
#         session=session,
#         model=models.Metric,
#         field="temp",
#         min_value=min_value,
#         max_value=max_value,
#         num_of_buckets=num_buckets,
#     )
