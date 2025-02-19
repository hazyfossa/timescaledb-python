# TimescaleDB for Python

Python Client for TimescaleDB -- an open-source time-series database built on PostgreSQL. This package is based on SQLModel and SQLAlchemy and designed to be used with FastAPI, Flask, and more.

Looking for Django? [Check out django-timescaledb](https://github.com/jamessewell/django-timescaledb)

## Installation

```bash
pip install timescaledb
```

## Usage 


### Create a TimescaleDB Model

The `TimescaleModel` class inherits from `SQLModel` but incldues a `time` field for TimescaleDB hypertables and an `id` field for primary keys.

`models.py`
```python
from sqlmodel import Field, SQLModel

from timescaledb import TimescaleModel

# create a model
class Metric(TimescaleModel, table=True):
    temp: float


class MetricCreate(Metric):
    # not a table but a Pydantic model
    temp: float


class MetricRead(Metric):
    # not a table but a Pydantic model
    id: int
    temp: float
    time: datetime = Field(default=None)
```


### Initialize the Database

The `timescaledb.create_engine` is a wrapper around `sqlmodel.create_engine` (which is a wrapper around `sqlalchemy.create_engine`) that ensures a timezone is set for your database. 

`database.py`
```python
import timescaledb
from sqlmodel import Session, SQLModel

DATABASE_URL = "postgresql://user:password@localhost:5432/timescaledb"
TIME_ZONE = "UTC"
ECHO_QUERIES = False

engine = timescaledb.create_engine(DATABASE_URL, timezone=TIME_ZONE, echo=ECHO_QUERIES)


def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    # Create all tables
    print("Creating database tables...")
    # automatically creates all tables that inherit from SQLModel
    SQLModel.metadata.create_all(engine)

    print("Creating hypertables...")
    # automatically creates hypertables for all models that inherit from TimescaleModel
    timescaledb.metadata.create_all(engine)

```


### Create a FastAPI App

Put it all together in a FastAPI app.

`main.py`
```python
from fastapi import FastAPI

from .database import init_db, get_session
from .models import Metric, MetricCreate, MetricRead

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/metrics/", response_model=MetricRead)
def create_metric(metric: MetricCreate, session: Session = Depends(get_session)):
    db_metric = models.Metric.from_orm(metric)
    session.add(db_metric)
    session.commit()
    session.refresh(db_metric)
    return db_metric


@app.get("/metrics/{metric_id}", response_model=MetricRead)
def read_metric(metric_id: int, session: Session = Depends(get_session)):
    metric = session.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, message="Metric not found")
    return metric


@app.get("/metrics/", response_model=list[MetricRead])
def list_metrics(session: Session = Depends(get_session)):
    metrics = session.query(Metric).all()
    return metrics
```

### Review the Sample Project


In [./sample_project](./sample_project) you can review a complete example that includes:
- A TimescaleDB model
- A FastAPI app
- Sample queries (`time_bucket_gapfill_query`, `time_bucket_query`)




