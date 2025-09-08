import pandas as pd
import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import tables, with_session


@st.cache_data
@with_session
def get_locations(session: Session, location_ids: pd.Series | list[int] = []) -> pd.DataFrame:
    query = select(tables.locations)

    if len(location_ids) > 0:
        query = query.where(tables.locations.c.id.in_(location_ids))

    results = session.execute(query).all()

    df = pd.DataFrame(results).set_index("id")

    # Remove useless columns
    df.drop(
        columns=[
            "address1",
            "address2",
            "horaires",
            "infos",
            "metro",
            "bus",
            "tram",
            "parking",
            "debut_infos",
            "fin_infos",
            "ville",
            "phone",
            "group_code",
        ],
        inplace=True,
    )

    return df


# @st.cache_data
@with_session
def get_collections(session: Session, is_active: bool = True) -> pd.DataFrame:
    query = select(tables.collection_groups)

    if is_active:
        query = query.where(tables.collection_groups.c.end_date >= func.now())

    results = session.execute(query).all()
    return pd.DataFrame(results).set_index("id")


# @st.cache_data
@with_session
def get_collection_snapshots(
    session: Session, collection_ids: pd.Series | list[int], only_last: bool = True
) -> pd.DataFrame:
    query = select(tables.collection_group_snapshots).where(
        tables.collection_group_snapshots.c.collection_group_id.in_(collection_ids)
    )

    if only_last:
        snap_subquery = (
            select(
                tables.collection_group_snapshots,
                func.row_number()
                .over(
                    partition_by=tables.collection_group_snapshots.c.collection_group_id,
                    order_by=tables.collection_group_snapshots.c.created_at.desc(),
                )
                .label("row_number"),
            )
        ).subquery()
        query = query.join(snap_subquery, snap_subquery.c.id == tables.collection_group_snapshots.c.id).where(
            snap_subquery.c.row_number == 1
        )

    query = query.order_by(tables.collection_group_snapshots.c.created_at.desc())

    results = session.execute(query).all()

    df = pd.DataFrame(results)
    if only_last:
        df = df.set_index("collection_group_id")
    else:
        df = df.set_index("id")
    return df


@st.cache_data
@with_session
def get_collection_events(session: Session, collection_ids: pd.Series | list[int]) -> pd.DataFrame:
    query = select(tables.collection_events).where(
        tables.collection_events.c.collection_group_id.in_(collection_ids),
        tables.collection_events.c.date >= func.now(),
    )
    results = session.execute(query).all()
    return pd.DataFrame(results).set_index("id")


@st.cache_data
@with_session
def get_event_schedules(session: Session, event_ids: pd.Series | list[int], only_last: bool = True) -> pd.DataFrame:
    query = select(tables.schedules).where(tables.schedules.c.event_id.in_(event_ids))

    if only_last:
        sch_subquery = (
            select(
                tables.schedules,
                func.row_number()
                .over(partition_by=tables.schedules.c.event_id, order_by=tables.schedules.c.created_at.desc())
                .label("row_number"),
            )
        ).subquery()

        query = query.join(sch_subquery, sch_subquery.c.id == tables.schedules.c.id).where(
            sch_subquery.c.row_number == 1
        )

    query = query.order_by(tables.schedules.c.created_at)

    results = session.execute(query).all()
    return pd.DataFrame(results).set_index("id")
