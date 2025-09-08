import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import dashboard.pages.home.services as services


def display_view(container: DeltaGenerator):
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
