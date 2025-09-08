import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import app.pages.home.panels as panels
import app.pages.home.services as services
from app.pages.home.sidebar import display_view as display_sidebar


def _event_details(container: DeltaGenerator):
    container.subheader("Évènement - détails", divider="red")
    selected_event = st.session_state.selected_event

    event_container = container.container(
        height=250 if selected_event is None else "stretch",
        horizontal_alignment="center" if selected_event is None else "left",
        vertical_alignment="center" if selected_event is None else "top",
        border=False,
    )

    if not selected_event:
        event_container.text("aucun évènement séléctionné.")
        return

    records = services.get_event_schedules(event_ids=[selected_event], only_last=False)
    last_record = records.iloc[-1]

    event_container.metric("Nombre de places", last_record.total_slots)

    event_container.line_chart(records, x="created_at", y="total_slots")

    event_container.dataframe(records)


def _collection_details(collection: pd.Series, container: DeltaGenerator = st):
    container.subheader("Collecte - détails", divider="red")

    collection_container = container.container(
        height=250 if collection.empty else "stretch",
        horizontal_alignment="center" if collection.empty else "left",
        vertical_alignment="center" if collection.empty else "top",
        border=False,
    )

    if collection.empty:
        collection_container.text("aucune collecte séléctionné.")
        return

    c1, c2 = collection_container.columns(2)
    c1.markdown(f"##### {collection.full_address}")
    subcontainer = c1.container(
        vertical_alignment="center",
        horizontal_alignment="left",
        horizontal=True,
    )
    subcontainer.text(f"Suivis depuis le {collection.created_at.strftime('%d/%m/%Y')}")
    subcontainer.link_button("Lien collecte", url=f"http://{collection.url_blood}", icon=":material/open_in_new:")
    panels.progress_start_in_days(collection, container=c2)

    snapshots = services.get_collection_snapshots([st.session_state.selected_collection], only_last=False)
    panels.area_fill_rate(snapshots, container=collection_container)


def _global_view(data: pd.DataFrame, container):
    # Row 1
    # panels.calendar_collections(data, container=container, height=300)

    container.subheader("Informations générale", divider="red")

    # Row 2
    # r2c1, r2c2 = container.columns([3, 2])
    panels.mean_slots_stats(data, container=container)

    # Row 3
    r3c1, r3c2 = container.columns([3, 2])
    panels.bar_next_collections(data, container=r3c1, height=300)
    panels.bar_day_of_week(data, container=r3c2, height=300)


def _get_data() -> pd.DataFrame:
    df_actives_collections = services.get_collections()
    df_locations = services.get_locations(location_ids=df_actives_collections.location_id)
    df_joined = df_actives_collections.join(df_locations, rsuffix="_location", on="location_id")

    df_snapshots = services.get_collection_snapshots(collection_ids=df_actives_collections.index.values)
    df_joined = df_joined.join(df_snapshots, rsuffix="_snap").sort_values(by=["start_date"])
    return df_joined


def display_page():
    try:
        st.set_page_config(
            page_title="Home | ma-collecte", page_icon="🩸", layout="wide", initial_sidebar_state="expanded"
        )

        # Data
        df = _get_data()

        main = st.container(border=None)
        sidebar = st.sidebar.container(width="stretch", border=None)

        display_sidebar(df, container=sidebar)

        # --- Collection ---
        # Selector

        # Details
        panels.map_locations(df, container=main, height=250)

        selected_collection = st.session_state.selected_collection
        collection = df.loc[selected_collection] if selected_collection else pd.Series()

        _global_view(df, container=main)
        _collection_details(collection, container=main)

        # --- Event ---
        # Selector
        _event_details(container=main)

        # Details

        print("end page")

    except Exception as e:
        print(f"Something went wrong: {e}")
        raise e
