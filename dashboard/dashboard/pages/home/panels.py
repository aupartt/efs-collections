from collections import defaultdict
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit_calendar import calendar

from dashboard.config import Colors


def count_collect_types(data: pd.DataFrame, container: DeltaGenerator = st, height: int = 500):
    for t, c in zip(st.session_state.collect_types.values(), st.columns(3)):
        count = data.loc[data[f"give_{t['en']}"], "n_collections"].sum()
        container.metric(t["fr"].capitalize(), count, height=int(height / 3), width="stretch", delta_color="normal")


def calendar_collections(data: pd.DataFrame, container: DeltaGenerator = st.container(), **kwargs) -> dict:
    df = data[["taux_remplissage", "city", "post_code", "start_date", "end_date"]].copy()

    calendar_options = {
        "headerToolbar": {"start": "title", "center": "", "end": "today prev,next"},
        "locale": "fr",
        "editable": True,
        "selectable": True,
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


def dataframe_collections(data: pd.DataFrame, container: DeltaGenerator = st, **kwargs) -> list[int]:
    df = data[["taux_remplissage", "city", "post_code", "start_date", "end_date"]].copy()

    df.taux_remplissage = df.taux_remplissage / 100
    df.post_code = df.post_code.str.slice(0, 2)

    column_config = {
        "taux_remplissage": st.column_config.ProgressColumn(
            "Taux de Remplissage", min_value=0, max_value=1
        ),  # st.column_config.NumberColumn("Taux de Remplissage", format="percent", width="small"),
        "city": st.column_config.TextColumn("Ville"),
        "post_code": st.column_config.TextColumn("CP", width=30),
        "start_date": st.column_config.DatetimeColumn("Débute le", format="DD/MM/YY", width="small"),
        "end_date": st.column_config.DatetimeColumn("Fini le", format="DD/MM/YY", width="small"),
    }

    selected = container.dataframe(
        df,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row",
        column_config=column_config,
        hide_index=True,
        **kwargs,
    )

    if len(selected.selection.rows) == 0:
        st.session_state.selected_collection = None
        st.session_state.selected_event = None
        return

    st.session_state.selected_collection = df.iloc[selected.selection.rows[0]].name


def dataframe_events(data: pd.DataFrame, container: DeltaGenerator = st):
    df = data.drop(columns=["lp_code", "created_at", "collection_group_id"])

    def _filter_date(serie: pd.Series, fn: callable):
        row = serie.values
        if row[0] is None:
            return row[1]
        elif row[1] is None:
            return row[0]
        return fn([row[0], row[1]])

    df["start_time"] = df[["morning_start_time", "afternoon_start_time"]].apply(_filter_date, fn=min, axis=1)
    df["end_time"] = df[["morning_end_time", "afternoon_end_time"]].apply(_filter_date, fn=max, axis=1)
    df = df.drop(columns=df.filter(regex=r"afternoon_|morning_").columns)

    column_config = {
        "date": st.column_config.DatetimeColumn("Date", format="DD/MM/YY", width="small"),
        "start_time": st.column_config.DatetimeColumn("Débute à", format="HH:mm", width="small"),
        "end_time": st.column_config.DatetimeColumn("Fini à", format="HH:mm", width="small"),
    }

    selected = container.dataframe(
        df,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row",
        column_config=column_config,
        hide_index=True,
    )

    if len(selected.selection.rows) == 0:
        st.session_state.selected_event = None
        return

    st.session_state.selected_event = df.iloc[selected.selection.rows[0]].name


def _create_layer(data: pd.DataFrame, collect_type: str):
    df = data[data[f"give_{collect_type}"]].to_dict("records")
    return pdk.Layer(
        type="IconLayer",
        data=df,
        get_icon="icon_data",
        get_size=20,
        get_position=["longitude", "latitude"],
        # get_color=Colors.List.red,
        get_radius=100,
        elevation_scale=10,
        elevation_range=[200, 1000],
        pickable=True,
        extruded=True,
        coverage=1,
        auto_highlight=True,
    )


def map_locations(data: pd.Series | pd.DataFrame, container: DeltaGenerator = st, **kwargs):
    df = data.copy()

    base_lat = 48.17
    base_lng = -2.9
    zoom = 6.7
    pitch = 0
    icon_data = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Blood_drop_plain.svg",
        "width": 150,
        "height": 150,
        "anchorY": 150,
    }

    # selected_collection = st.session_state.selected_collection
    if isinstance(df, pd.Series):
        df = pd.DataFrame([df])
        base_lat = df.latitude.mean()
        base_lng = df.longitude.mean()
        zoom = 13
        pitch = 0

    df["icon_data"] = None
    df.icon_data = df.icon_data.apply(lambda x: icon_data)
    df.start_date = df.start_date.dt.strftime("%d/%m/%Y")
    df.end_date = df.end_date.apply(lambda x: x.strftime("%d/%m/%Y"))

    layers = [_create_layer(df, collect_type) for collect_type in ["blood", "plasma", "platelet"]]

    # View state
    view_state = pdk.ViewState(
        latitude=base_lat,
        longitude=base_lng,
        zoom=zoom,
        pitch=pitch,
    )

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

    subcontainer = container.container(
        height=height,
        vertical_alignment="distribute",
        border=False,
    )
    subcontainer.markdown("**Collectes les prochaines semaines**")
    subcontainer.bar_chart(
        df,
        x="semaine",
        y="created_at",
        x_label="Semaine",
        y_label="Collectes",
        color=Colors.Str.lightred,
        height=min(500, height - 45),
        **kwargs,
    )


def area_fill_rate(data: pd.DataFrame, container: DeltaGenerator = st, height: int = 500):
    df = data[["created_at", "nb_places_reservees_st", "nb_places_restantes_st", "nb_places_totales_st"]].copy()
    df.rename(columns={"created_at": "Date", "nb_places_reservees_st": "Places réservées"}, inplace=True)

    container.markdown("**Places réservées dans le temps**")
    chart = (
        alt.Chart(df)
        .mark_area(line={"color": "primary"}, point={"size": 15}, height=min(500, height - 45))
        .encode(
            alt.X("Date").axis(format="%d/%m/%y"),
            alt.Y("Places réservées").scale(domain=[0, df.nb_places_totales_st.max()]),
        )
    )
    container.altair_chart(chart)


def bar_day_of_week(data: pd.DataFrame, container: DeltaGenerator = st, height: int = 500):
    df = data[["efs_id", "start_date", "end_date"]].copy()

    # day_map = {0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"}

    day_dict = defaultdict(int)
    for _, row in df.iterrows():
        dt_day = (row.end_date.date() - row.start_date.date()).days
        for i in range(dt_day + 1):
            d = row.start_date + timedelta(days=i)
            # day_dict[day_map[d.dayofweek]] += 1
            day_dict[d.dayofweek] += 1

    # TODO: Find how to make bar_chart not sorting by default
    container.markdown("**Nombre de collectes pour chaque jours de la semaine**")
    container.bar_chart(
        day_dict,
        x_label="Jour de la semaine",
        y_label="Nombre totale de collectes",
        color=Colors.Str.darkred,
        height=min(500, height - 45),
    )


def mean_slots_stats(data: pd.DataFrame, container: DeltaGenerator = st):
    df = data[["start_date", "end_date", "taux_remplissage", "nb_places_totales_st"]].copy()

    mean_duration_days = df.end_date.dt.date - df.start_date.dt.date + timedelta(days=1)
    mean_duration_days = mean_duration_days.apply(lambda x: x.days)

    # metric mean
    # container.markdown("**Moyennes**")
    _container = container.container(
        width="stretch",
        height="stretch",
        vertical_alignment="center",
        horizontal_alignment="left",
    )
    subcontainer = _container.container(width="stretch", height="content", horizontal=True)
    subcontainer.metric("Durée d'une collecte", f"{round(mean_duration_days.mean(), 2)} jours")
    subcontainer.metric("Nombre de places", f"{round(df.nb_places_totales_st.mean())} places")
    subcontainer.metric("Taux de remplissage", f"{round(df.taux_remplissage.mean())}%")

    fill_rate_next_week = df.loc[df.end_date <= (datetime.now() + timedelta(days=7)), "taux_remplissage"].mean()
    subcontainer.metric("Taux de remplissage (7j)", f"{round(fill_rate_next_week)}%")


def progress_start_in_days(collection: pd.DataFrame, container: DeltaGenerator = st):
    total_days = (collection.start_date.date() - collection.created_at.date()).days
    current_days = (datetime.now().date() - collection.created_at.date()).days

    dt_days = total_days - current_days
    text = f"dans **{dt_days}j**" if dt_days > 0 else "aujourd'hui"
    container.markdown(
        f"""
    <style>
    .stProgress > div:nth-child(2) > div > div > div {{
        background-color: {Colors.Str.lightred};
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
    rate = current_days / total_days
    container.progress(min(rate, 1.0), f"Débute {text}")


def event_base_metrics(data: pd.DataFrame, container: DeltaGenerator = st):
    last_record = data.iloc[-1]

    subc = container.container(horizontal=True, horizontal_alignment="center")
    subc.metric("Places totale", last_record.total_slots)
    subc.metric("De", last_record.timetable_min.strftime("%H:%M"))
    subc.metric("à", last_record.timetable_max.strftime("%H:%M"))
