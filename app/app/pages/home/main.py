from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import app.pages.home.panels as panels
import app.pages.home.services as services


def display_table(data: list, **kwargs):
    result = st.dataframe(data, **kwargs)
    if isinstance(result, dict):
        print("result:", result)
        return result.selection.rows


def _collection_details(collection: pd.Series, container: DeltaGenerator = st):
    collection_container = container.container(
        height=250 if collection.empty else "stretch",
        horizontal_alignment="center" if collection.empty else "left",
        vertical_alignment="center" if collection.empty else "top",
        border=False,
    )

    collection_container.subheader("Collecte - détails", divider="red")
    c1, c2 = collection_container.columns(2)
    c1.markdown(f"##### {collection.full_address}")
    subcontainer = c1.container(
        vertical_alignment="center",
        horizontal_alignment="left",
        horizontal=True,
    )
    subcontainer.text(f"Suivis depuis le {collection.created_at.strftime('%d/%m/%Y')}")
    subcontainer.link_button("Lien collecte", url=f"http://{collection.url_blood}", icon=":material/open_in_new:")

    total_days = (collection.start_date.date() - collection.created_at.date()).days
    current_days = (datetime.now().date() - collection.created_at.date()).days

    # st.write(type(res), res)
    c2.progress(current_days / total_days, f"Débute dans **{total_days - current_days}j**")

    snapshots = services.get_collection_snapshots([st.session_state.selected_collection], only_last=False)
    panels.area_chart_fill_rate(snapshots, container=collection_container)


def _global_view(data: pd.DataFrame, container):
    container.subheader("Informations générale", divider="red")

    # Row 1
    panels.calendar_collections(data, container=container, height=300)

    # Row 2
    r2c1, r2c2 = container.columns([3, 2])
    panels.bar_next_collections(data, container=r2c1, height=300)
    panels.mean_slots_stats(data, container=r2c2)

    # Row 3
    r3c1, r3c2 = container.columns([3, 2])
    panels.bar_day_of_week(data, container=r3c2)


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
        st.sidebar.title("Futures collectes mobiles (EFS) en Bretagne.")

        # Data
        df = _get_data()

        main = st.container(border=None)
        sidebar = st.sidebar.container(width="stretch", border=None)

        # --- Collection ---
        # Selector
        sidebar.subheader("Collectes", divider="red")
        panels.table_collections(df, container=sidebar, height=500)

        # Details
        panels.map_locations(df, container=main, height=250)

        selected_collection = st.session_state.selected_collection
        collection = df.loc[selected_collection] if selected_collection else pd.Series()

        if collection.empty:
            _global_view(df, main)
        else:
            _collection_details(collection, main)

        # --- Event ---
        # Selector

        sidebar.subheader("Évènements", divider="red")
        event_list_container = sidebar.container(
            height=100 if collection.empty else "stretch",
            horizontal_alignment="center" if collection.empty else "left",
            vertical_alignment="center" if collection.empty else "top",
            border=False,
        )

        if not collection.empty:
            events = services.get_collection_events(collection_ids=[selected_collection])
            event_list_container.dataframe(events)
        else:
            event_list_container.text("aucune collecte séléctionné.")

        # Details

        print("end page")

    except Exception as e:
        print(f"Something went wrong: {e}")
        raise e
