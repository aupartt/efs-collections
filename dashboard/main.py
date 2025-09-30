import streamlit as st

from dashboard.config import ST_SESSION_STATE
from dashboard.pages import active_page, home_page


def init():
    if len(st.session_state.keys()) == 0:
        st.session_state.update(ST_SESSION_STATE)  # type: ignore


def main():
    init()

    p1 = st.Page(home_page, title="Home", icon="🩸", url_path="/home")
    p2 = st.Page(active_page, title="Collectes actives", icon="📊", url_path="/active")
    # p3 = st.Page(historic_page, title="Historique", icon="📅", url_path="/historic")
    pg = st.navigation([p1, p2], position="top")
    pg.run()


if __name__ == "__main__":
    main()
