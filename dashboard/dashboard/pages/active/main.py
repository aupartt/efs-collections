import pandas as pd
import streamlit as st

import dashboard.services as services
from dashboard.pages.active.views import display_collection_details, display_event_details, display_sidebar


def _get_data() -> pd.DataFrame:
    df_actives_collections = services.get_collections()
    df_locations = services.get_locations(location_ids=df_actives_collections.location_id)
    df_joined = df_actives_collections.join(df_locations, rsuffix="_location", on="location_id")

    df_snapshots = services.get_collection_snapshots(collection_ids=df_actives_collections.index.to_list())
    df_joined = df_joined.join(df_snapshots, rsuffix="_snap").sort_values(by=["start_date"])
    return df_joined


def display_page():
    st.set_page_config(page_title="Home | ma-collecte", page_icon="🩸", layout="wide", initial_sidebar_state="expanded")

    # Data
    df = _get_data()

    main = st.container(border=None)
    sidebar = st.sidebar.container(width="stretch", border=None)

    # Sidebar
    display_sidebar(df, container=sidebar)

    main.title("Informations sur les collectes actives.")

    # Views
    display_collection_details(df, container=main)  # type: ignore
    display_event_details(container=main)
