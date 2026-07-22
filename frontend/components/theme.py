import streamlit as st


def initialize_theme():

    if "theme" not in st.session_state:

        st.session_state.theme = "light"


def toggle_theme():

    if st.session_state.theme == "light":

        st.session_state.theme = "dark"

    else:

        st.session_state.theme = "light"


def current_theme():

    return st.session_state.theme