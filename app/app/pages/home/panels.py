from collections import defaultdict
from datetime import timedelta

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit_calendar import calendar

# from app.config import Colors


def collect_types_count(data: pd.DataFrame, container: DeltaGenerator = st, height: int = 500):
    for t, c in zip(st.session_state.collect_types.values(), st.columns(3)):
        count = data.loc[data[f"give_{t['en']}"], "n_collections"].sum()
        container.metric(t["fr"].capitalize(), count, height=int(height / 3), width="stretch", delta_color="normal")


def calendar_collections(data: pd.DataFrame, container: DeltaGenerator = st.container(), **kwargs) -> dict:
    df = data[["taux_remplissage", "city", "post_code", "start_date", "end_date"]].copy()

    calendar_options = {
        "headerToolbar": {"start": "title", "center": "", "end": "today prev,next"},
        "locale": "fr",
        # "editable": True,
        # "selectable": True,
        "initialView": "timelineMonth",
        # "showNonCurrentDates": True,
        # "fixedWeekCount": False,
        # "firstDay": 1,
        "eventBackgroundColor": "#ff4b4b",
        # "eventTextColor": "#ff4b4b",
        "eventBorderColor": "black",
        **kwargs,
    }

    calendar_events = [
        {
            "title": f"{event.city}",
            "start": event.start_date.strftime("%Y-%m-%d"),
            "end": event.end_date.strftime("%Y-%m-%d"),
            "id": idx,
        }
        for idx, event in df.iterrows()
    ]

    custom_css = """
        .fc {
            font-size: 0.8rem;
            scrollbar-width: thin;
            scrollbar-height: thin;
            scrollbar-color: rgba(250, 250, 250, 0.4) transparent;
            --fc-border-color: #424242;
            --fc-today-bg-color: #ff4b4b42;
            // --fc-highlight-color: #ff4b4b9b;
            --fc-button-bg-color: #ff8c8c9b;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 1.3rem;
            text-transform: capitalize;
        }
    """

    with container:
        selected = calendar(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            callbacks=[],  # ["eventClick"],
            key="calendar",  # Assign a widget key to prevent state loss
        )
        if selected:
            st.session_state["selected_collection"] = int(selected["eventClick"]["event"]["id"])
            st.write(st.session_state.selected_collection)


def table_collections(data: pd.DataFrame, container: DeltaGenerator = st, **kwargs) -> list[int]:
    df = data[["taux_remplissage", "city", "post_code", "start_date", "end_date"]].copy()

    df.taux_remplissage = df.taux_remplissage / 100
    column_config = {
        "taux_remplissage": st.column_config.ProgressColumn(
            "Taux de Remplissage", min_value=0, max_value=1
        ),  # st.column_config.NumberColumn("Taux de Remplissage", format="percent", width="small"),
        "city": st.column_config.TextColumn("Ville", width="medium"),
        "post_code": st.column_config.TextColumn("CP", width="small"),
        "start_date": st.column_config.DatetimeColumn("Débute le", format="DD/MM/YYYY", width="small"),
        "end_date": st.column_config.DatetimeColumn("Fini le", format="DD/MM/YYYY", width="small"),
        "n_collections": st.column_config.NumberColumn("Nombre de collectes", format="accounting", width="small"),
        # "id": st.column_config.NumberColumn(
        #     "Collecte ID",
        #     width="small",
        # ),
        "collection_id": st.column_config.NumberColumn("Collecte ID", width="small"),
    }

    selected = container.dataframe(
        df,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row",
        column_config=column_config,
        **kwargs,
    )

    if len(selected.selection.rows) == 0:
        st.session_state.selected_collection = None
        return

    st.session_state.selected_collection = df.iloc[selected.selection.rows[0]].name


def _create_layer(data: pd.DataFrame, collect_type: str):
    df = data[data[f"give_{collect_type}"]].to_dict("records")
    return pdk.Layer(
        type="IconLayer",
        data=df,
        get_icon="icon_data",
        get_size=20,
        get_position=["longitude", "latitude"],
        # get_color=Colors.List.lightred,
        get_radius=100,
        elevation_scale=10,
        elevation_range=[200, 1000],
        pickable=True,
        extruded=True,
        coverage=1,
        auto_highlight=True,
    )


def map_locations(data: pd.DataFrame, container: DeltaGenerator = st, **kwargs):
    df = data.copy()

    base_lat = 48.17
    base_lng = -2.9
    zoom = 6.7
    pitch = 0

    selected_collection = st.session_state.selected_collection
    if selected_collection:
        df = df.loc[[selected_collection]]
        base_lat = df.latitude.mean()
        base_lng = df.longitude.mean()
        zoom = 13
        pitch = 0

    icon_data = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Blood_drop_plain.svg",
        "width": 150,
        "height": 150,
        "anchorY": 150,
    }
    df["icon_data"] = None
    df.icon_data = df.icon_data.apply(lambda x: icon_data)
    df.start_date = df.start_date.dt.strftime("%d/%m/%Y")
    df.end_date = df.end_date.apply(lambda x: x.strftime("%d/%m/%Y"))

    layers = [_create_layer(df, collect_type) for collect_type in ["blood", "plasma", "platelet"]]

    # View state
    view_state = pdk.ViewState(latitude=base_lat, longitude=base_lng, zoom=zoom, pitch=pitch)

    # Deck with tooltip
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={"text": "{full_address}\nDu {start_date} au {end_date}"},  # Événements: {n_collections}\n
        map_style="dark" if st.context.theme.type == "dark" else "road",
    )

    return container.pydeck_chart(deck, **kwargs)


def bar_next_collections(data: pd.DataFrame, container: DeltaGenerator = st, height: int = 500, **kwargs):
    df = data[["start_date", "created_at"]].copy()

    df["semaine"] = df.start_date.apply(lambda x: x.week)
    df.semaine = df.semaine - df.semaine.min()

    df = df.groupby("semaine").aggregate({"semaine": "mean", "created_at": "count"})
    df.rename(columns={"created_at": "Collectes", "semaine": "Semaine"}, inplace=True)

    subcontainer = container.container(height=height, vertical_alignment="distribute", border=False)
    subcontainer.markdown("**Collectes les prochaines semaines**")
    subcontainer.bar_chart(df, x="Semaine", y="Collectes", height=min(500, height - 45), **kwargs)


def area_chart_fill_rate(data: pd.DataFrame, container: DeltaGenerator = st):
    df = data[["created_at", "nb_places_reservees_st", "nb_places_restantes_st", "nb_places_totales_st"]].copy()
    df.rename(columns={"created_at": "Date", "nb_places_reservees_st": "Places réservées"}, inplace=True)

    container.markdown("**Inscriptions dans le temps**")
    chart = (
        alt.Chart(df)
        .mark_area(line={"color": "primary"}, point={"size": 15})
        .encode(
            alt.X("Date").axis(format="%d/%m/%y"),
            alt.Y("Places réservées").scale(domain=[0, df.nb_places_totales_st.max()]),
        )
    )
    container.altair_chart(chart)


def bar_day_of_week(data: pd.DataFrame, container: DeltaGenerator = st):
    df = data[["efs_id", "start_date", "end_date"]].copy()

    day_map = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"}

    day_dict = defaultdict(int)
    for _, row in df.iterrows():
        dt_day = (row.end_date.date() - row.start_date.date()).days
        for i in range(dt_day + 1):
            d = row.start_date + timedelta(days=i)
            day_dict[day_map[d.dayofweek]] += 1

    # TODO: Find how to make bar_chart not sorting by default
    container.markdown("**Nombre de collectes pour chaque jours de la semaine**")
    container.bar_chart(day_dict)


def mean_slots_stats(data: pd.DataFrame, container: DeltaGenerator = st):
    df = data[["start_date", "end_date", "taux_remplissage", "nb_places_totales_st"]].copy()

    mean_duration_days = df.end_date.dt.date - df.start_date.dt.date + timedelta(days=1)
    mean_duration_days = mean_duration_days.apply(lambda x: x.days)

    # metric mean
    # container.markdown("**Moyennes**")
    _container = container.container(
        width="stretch", height="stretch", vertical_alignment="center", horizontal_alignment="center"
    )
    subcontainer = _container.container(width=600, height="content", horizontal=True)
    subcontainer.metric("Durée moyenne", f"{round(mean_duration_days.mean(), 2)} jours")
    subcontainer.metric("Places moyenne", f"{round(df.nb_places_totales_st.mean())} places")
    subcontainer.metric("Taux remplissage moyen", f"{round(df.taux_remplissage.mean())}%")
