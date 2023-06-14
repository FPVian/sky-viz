import streamlit as st


def sidebar():
    st.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )
