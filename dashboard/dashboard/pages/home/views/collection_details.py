import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import dashboard.pages.home.panels as panels
import dashboard.pages.home.services as services


def display_view(collection: pd.Series, container: DeltaGenerator = st):
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

    c1, c2 = collection_container.columns([1, 2], gap="large")
    c1.markdown(f"##### {collection.full_address}")
    subcontainer = c1.container(
        vertical_alignment="center",
        horizontal_alignment="left",
        horizontal=True,
    )
    subcontainer.text(f"Suivis depuis le {collection.created_at.strftime('%d/%m/%Y')}")
    subcontainer.link_button("Lien collecte", url=f"http://{collection.url_blood}", icon=":material/open_in_new:")

    c1.html("<br><br>")
    panels.progress_start_in_days(collection, container=c1)
    panels.map_locations(collection, container=c2, height=250)

    panels.divider(container=collection_container)

    c1, c2 = collection_container.columns([1, 6])
    records = services.get_collection_snapshots([st.session_state.selected_collection], only_last=False)
    last_record = records.iloc[-1]
    m_subc = c1.container(height=350, border=False, vertical_alignment="distribute")
    m_subc.metric("Places totales", last_record.nb_places_totales_st)
    m_subc.metric("Places réservées", last_record.nb_places_reservees_st)
    m_subc.metric("Places restantes", last_record.nb_places_restantes_st)

    panels.area_fill_rate(records, container=c2, height=250)
