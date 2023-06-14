import streamlit as st


def configure_page():
    st.set_page_config(
        page_title='Flight Data',
        page_icon='✈️',
        layout='wide',
        menu_items={
            'Get help': 'mailto:ian@skyviz.app?subject=SkyViz%20Help',
            'About': '''
                ### Github
                - [Source](https://www.github.com/fpvian/flight-data)

                - [Creator's Profile](https://www.github.com/fpvian)

                ### Data Source
                - ADSBexchange.com, https://ADSBexchange.com
                ---
                ''',
        },
    )
    st.title('Flight Data')
