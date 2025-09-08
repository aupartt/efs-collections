import pandas as pd
import streamlit as st

import app.pages.home.panels as panels
import app.pages.home.services as services
from app.pages.home.views import display_collection_details, display_event_details, display_sidebar


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

        # Sidebar
        display_sidebar(df, container=sidebar)

        # --- Collection ---
        # Selector

        # Details
        panels.map_locations(df, container=main, height=250)

        selected_collection = st.session_state.selected_collection
        collection = df.loc[selected_collection] if selected_collection else pd.Series()

        # Row 1
        # panels.calendar_collections(data, container=container, height=300)
        main.subheader("Informations générale", divider="red")

        # Row 2
        # r2c1, r2c2 = container.columns([3, 2])
        panels.mean_slots_stats(df, container=main)

        # Row 3
        r3c1, r3c2 = main.columns([3, 2])
        panels.bar_next_collections(df, container=r3c1, height=300)
        panels.bar_day_of_week(df, container=r3c2, height=300)

        display_collection_details(collection, container=main)
        display_event_details(container=main)

        print("end page")

    except Exception as e:
        print(f"Something went wrong: {e}")
        raise e
