from typing import Callable, Concatenate, ParamSpec, TypeVar

from sqlalchemy import MetaData, Table
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dashboard.core.settings import settings

engine = None
SessionLocal = None

metadata = MetaData()


# Postgres tables
class tables:
    groups = Table("groups", metadata, autoload_with=engine)
    locations = Table("locations", metadata, autoload_with=engine)
    collection_groups = Table("collection_groups", metadata, autoload_with=engine)
    collection_group_snapshots = Table("collection_group_snapshots", metadata, autoload_with=engine)
    collection_events = Table("collection_events", metadata, autoload_with=engine)
    schedules = Table("schedules", metadata, autoload_with=engine)


P = ParamSpec("P")
R = TypeVar("R")


def with_session(fn: Callable[Concatenate[Session, P], R]) -> Callable[P, R]:
    """Function decorator to get database session"""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        global engine, SessionLocal

        if engine is None:
            engine = create_engine(settings.POSTGRES_URL, pool_size=10, max_overflow=20)
        if SessionLocal is None:
            SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

        with SessionLocal() as session:
            try:
                return fn(session, *args, **kwargs)
            finally:
                session.close()

    return wrapper
