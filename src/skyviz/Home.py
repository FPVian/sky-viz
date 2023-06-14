from skyviz.config.settings import s
from database.models import FlightSamples
from skyviz.db.base_repo import BaseRepository
from skyviz.utils import logger
from skyviz.sections.sidebar import sidebar

import streamlit as st
import pandas as pd
from hydra.utils import instantiate

from datetime import timedelta

log = logger.create(__name__)

'''
Streamlit API reference: https://docs.streamlit.io/library/api-reference
'''


def main():
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

    @st.cache_resource
    def init_db_connection() -> BaseRepository:
        log.info('caching database connection')
        return instantiate(s.db)

    @st.cache_data(ttl=timedelta(minutes=30))
    def read_flight_samples() -> pd.DataFrame:
        log.info('caching flight samples table')
        db = init_db_connection()
        table = pd.read_sql_table(FlightSamples.__tablename__, db.engine)
        return table

    flight_samples_data = read_flight_samples()

    st.subheader('Map of flights within 1,000km of Denver International Airport')
    st.map(flight_samples_data)

    with st.sidebar:
        sidebar()

    left_column, right_column = st.columns(2)

    with left_column:
        st.write('this is a left column')

    with right_column:
        st.write('this is a right column')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
