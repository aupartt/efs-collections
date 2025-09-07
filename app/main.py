import streamlit as st

from app.config import ST_SESSION_STATE
from app.pages.home import display_page


def init():
    if len(st.session_state.keys()) == 0:
        st.session_state.update(ST_SESSION_STATE)


def main():
    try:
        init()
        display_page()
    except Exception as e:
        print(f"ERROR: {e}")
        raise e


if __name__ == "__main__":
    main()
