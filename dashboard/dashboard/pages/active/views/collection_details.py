import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import dashboard.pages.active.panels as panels
import dashboard.services as services


def display_view(data: pd.DataFrame, container: DeltaGenerator = st.container()):
    container.subheader("Collecte - détails", divider="red")

    selected_collection = st.query_params.get("selected_collection", None)
    if st.session_state.selected_collection is not None:
        selected_collection = st.session_state.selected_collection

    collection_container = container.container(
        height=250 if selected_collection is None else "stretch",
        horizontal_alignment="center" if selected_collection is None else "left",
        vertical_alignment="center" if selected_collection is None else "top",
        border=False,
    )

    if selected_collection is None:
        collection_container.text("aucune collecte séléctionné.")
        return

    collection = data.loc[int(selected_collection)] if selected_collection else pd.Series()

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
    panels.progress_start_in_days(collection, container=c1)  # type: ignore
    panels.map_locations(collection, container=c2, height=250)

    panels.divider(container=collection_container)

    c1, c2 = collection_container.columns([1, 6])
    records = services.get_collection_snapshots([int(selected_collection)], only_last=False)
    last_record = records.iloc[-1]
    m_subc = c1.container(height=350, border=False, vertical_alignment="distribute")
    m_subc.metric("Places totales", last_record.nb_places_totales_st)
    m_subc.metric("Places réservées", last_record.nb_places_reservees_st)
    m_subc.metric("Places restantes", last_record.nb_places_restantes_st)

    panels.area_fill_rate(records, container=c2, height=250)
