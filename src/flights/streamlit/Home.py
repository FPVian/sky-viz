from flights.streamlit.sections.sidebar import sidebar

import streamlit as st

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

with st.sidebar:
    sidebar()
