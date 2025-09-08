from sqlalchemy import MetaData, Table
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

engine = create_engine(settings.POSTGRES_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

metadata = MetaData()


# Postgres tables
class tables:
    groups = Table("groups", metadata, autoload_with=engine)
    locations = Table("locations", metadata, autoload_with=engine)
    collection_groups = Table("collection_groups", metadata, autoload_with=engine)
    collection_group_snapshots = Table("collection_group_snapshots", metadata, autoload_with=engine)
    collection_events = Table("collection_events", metadata, autoload_with=engine)
    schedules = Table("schedules", metadata, autoload_with=engine)


def with_session(fn):
    """Function decorator to get database session"""

    def wrapper(*args, **kwargs):
        with SessionLocal() as session:
            try:
                return fn(session, *args, **kwargs)
            except Exception as e:
                print(f"Something went wrong with PostGres: {str(e)}")
            finally:
                session.close()

    return wrapper
