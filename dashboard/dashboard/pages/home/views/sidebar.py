import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import dashboard.pages.home.panels as panels
import dashboard.pages.home.services as services


def display_view(data: pd.DataFrame, container: DeltaGenerator):
    container.subheader("Collectes", divider="red")
    panels.dataframe_collections(data, container=container, height=500)

    selected_collection = st.session_state.selected_collection
    collection = data.loc[selected_collection] if selected_collection else pd.Series()

    container.subheader("Évènements", divider="red")
    event_list_container = container.container(
        height=100 if collection.empty else "stretch",
        horizontal_alignment="center" if collection.empty else "left",
        vertical_alignment="center" if collection.empty else "top",
        border=False,
    )

    if not collection.empty:
        events = services.get_collection_events(collection_ids=[selected_collection])
        panels.dataframe_events(events, container=event_list_container)
    else:
        event_list_container.text("aucune collecte séléctionné.")
