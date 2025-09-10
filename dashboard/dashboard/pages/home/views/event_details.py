import streamlit as st
from streamlit.delta_generator import DeltaGenerator

import dashboard.pages.home.panels as panels
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

    panels.event_base_metrics(records, container=event_container)

    panels.divider(container=event_container)

    c1, c2 = event_container.columns([2, 2])
    c1.markdown("**Places disponibles**")
    c1.line_chart(records, x="created_at", y="total_slots")
    panels.event_schedules(records, container=c2)
