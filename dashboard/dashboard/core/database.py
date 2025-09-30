from typing import Callable, Concatenate, ParamSpec, TypeVar

from pydantic import BaseModel
from sqlalchemy import Engine, MetaData, Table
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dashboard.core.settings import settings

_engine = None
_SessionLocal = None


def _init_db_engine() -> tuple[Engine, sessionmaker]:
    """Initialize the database engine and session factory."""
    global _engine, _SessionLocal

    if _engine is None:
        _engine = create_engine(settings.POSTGRES_URL, pool_size=10, max_overflow=20)
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

    return _engine, _SessionLocal


class Tables(BaseModel):
    groups: Table
    locations: Table
    collection_groups: Table
    collection_group_snapshots: Table
    collection_events: Table
    schedules: Table

    class Config:
        arbitrary_types_allowed = True


def get_tables() -> Tables:
    """Create all Table connection and return a Tables model."""
    engine, _ = _init_db_engine()

    metadata = MetaData()

    tables = Tables(
        groups=Table("groups", metadata, autoload_with=engine),
        locations=Table("locations", metadata, autoload_with=engine),
        collection_groups=Table("collection_groups", metadata, autoload_with=engine),
        collection_group_snapshots=Table("collection_group_snapshots", metadata, autoload_with=engine),
        collection_events=Table("collection_events", metadata, autoload_with=engine),
        schedules=Table("schedules", metadata, autoload_with=engine),
    )
    return tables


P = ParamSpec("P")
R = TypeVar("R")


def with_session(fn: Callable[Concatenate[Session, P], R]) -> Callable[P, R]:
    """Function decorator to get database session"""

    _, SessionLocal = _init_db_engine()

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with SessionLocal() as session:
            try:
                return fn(session, *args, **kwargs)
            finally:
                session.close()

    return wrapper
