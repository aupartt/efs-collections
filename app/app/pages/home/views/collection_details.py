import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import app.pages.home.panels as panels
import app.pages.home.services as services


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
