import pandas as pd
import streamlit as st

import dashboard.pages.home.panels as panels
import dashboard.services as services


def _get_data() -> pd.DataFrame:
    df_actives_collections = services.get_collections()
    df_locations = services.get_locations(location_ids=df_actives_collections.location_id)
    df_joined = df_actives_collections.join(df_locations, rsuffix="_location", on="location_id")

    df_snapshots = services.get_collection_snapshots(collection_ids=df_actives_collections.index.to_list())
    df_joined = df_joined.join(df_snapshots, rsuffix="_snap").sort_values(by=["start_date"])
    return df_joined


def display_page():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

    # Data
    df = _get_data()

    main = st.container(border=None)

    main.title("Collectes mobiles (EFS) en Bretagne.")

    # main.subheader("Informations générale", divider="red")

    panels.mean_slots_stats(df, container=main)

    panels.divider(container=main)

    c1, c2 = main.columns([2, 3])
    panels.map_locations(df, container=c1, height=400)
    panels.calendar_collections(df, container=c2, height=400)

    panels.divider(container=main)

    c1, c2 = main.columns([3, 2])
    panels.bar_next_collections(df, container=c1, height=400)
    panels.bar_day_of_week(df, container=c2, height=400)
