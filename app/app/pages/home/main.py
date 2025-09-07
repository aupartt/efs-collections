from datetime import datetime

import pandas as pd
import streamlit as st

import app.pages.home.panels as panels
import app.pages.home.services as services


def display_table(data: list, **kwargs):
    result = st.dataframe(data, **kwargs)
    if isinstance(result, dict):
        print("result:", result)
        return result.selection.rows


def _collection_details(collection: pd.Series, container=st):
    collection_container = container.container(
        height="stretch",
        horizontal_alignment="center" if collection.empty else "left",
        vertical_alignment="center" if collection.empty else "top",
        border=False,
    )
    if not collection.empty:
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
        # panels.calendar_collections(collection, container=c2, height=500)

        snapshots = services.get_collection_snapshots([st.session_state.selected_collection], only_last=False)
        panels.area_chart_fill_rate(snapshots, container=collection_container)
    else:
        collection_container.text("aucune collecte séléctionné.")


def display_page():
    try:
        st.set_page_config(page_title="Home", page_icon="🌍", layout="wide")
        st.sidebar.title("Futures collectes mobiles (EFS) en Bretagne.")

        # Data
        df_actives_collections = services.get_collections()
        df_locations = services.get_locations(location_ids=df_actives_collections.location_id)
        df_joined = df_actives_collections.join(df_locations, rsuffix="_location", on="location_id")

        df_snapshots = services.get_collection_snapshots(collection_ids=df_actives_collections.index.values)
        df_joined = df_joined.join(df_snapshots, rsuffix="_snap").sort_values(by=["start_date"])

        c2 = st.container(border=None)
        c1 = st.sidebar.container(width="stretch")

        panels.hist_next_collections(df_joined, container=c1, height=250)

        # --- Collection ---
        # Selector
        c1.subheader("Collectes - liste", divider="red")
        panels.table_collections(df_joined, container=c1, height=500)

        # Details
        panels.map_locations(df_joined, container=c2, height=250)
        c2.subheader("Collectes - détails", divider="red")
        selected_collection = st.session_state.selected_collection
        collection = df_joined.loc[selected_collection] if selected_collection else pd.Series()

        _collection_details(collection, c2)

        # --- Event ---
        # Selector
        c1.subheader("Évènement - liste", divider="red")
        event_list_container = c1.container(
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
