import streamlit as st

'''
Implementation:
from skyviz.sections.sidebar import sidebar
with st.sidebar:
    sidebar()
'''


def sidebar():
    st.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )
