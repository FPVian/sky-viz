from flights.streamlit.sections.sidebar import sidebar

import streamlit as st

from datetime import timedelta

st.set_page_config(
    page_title='Flight Data',
    page_icon='✈️',
    layout='wide',
    menu_items={
        'Get help': 'mailto:distantdollars@gmail.com?subject=Flight%20Data%20Help',
        'About': '''
            ### Github
            [Source](https://www.github.com/fpvian/flight-data)

            [Creator's Profile](https://www.github.com/fpvian)

            ---
            ''',
        },
    )

st.title('Flight Data')

@st.cache_resource
def init_db_connection():
    pass

@st.cache_data(ttl=timedelta(minutes=60))
def fetch_data(_db_connection):
    pass

with st.sidebar:
    sidebar()

left_column, right_column = st.columns(2)

with left_column:
    pass

with right_column:
    pass
