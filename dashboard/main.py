import streamlit as st

from dashboard.config import ST_SESSION_STATE
from dashboard.pages.home import display_page


def init():
    if len(st.session_state.keys()) == 0:
        st.session_state.update(ST_SESSION_STATE)


def main():
    try:
        init()
        display_page()
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
