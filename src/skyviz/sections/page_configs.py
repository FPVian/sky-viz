import streamlit as st


def configure_home_page():
    st.set_page_config(
        page_title='SkyViz',
        page_icon='✈️',
        layout='wide',
        menu_items={
            'Get help': 'mailto:ian@skyviz.app?subject=SkyViz%20Help',
            'Report a Bug': 'https://www.github.com/fpvian/flight-data',
            'About': '''
                ### [Creator's Github Profile](https://www.github.com/fpvian)

                ### Data Source
                - ADSBexchange.com, https://ADSBexchange.com
                ---
                ''',
        },
    )
    st.title('Flights Data Tracker')
