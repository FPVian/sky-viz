from skyviz.sections.page_configs import configure_home_page
from skyviz.data.cached_functions import init_db
from skyviz.utils import logger
from database.models import FlightSamples

import streamlit as st
from sqlalchemy.orm import Session

log = logger.create(__name__)


def main():
    '''
    Streamlit API reference: https://docs.streamlit.io/library/api-reference
    '''
    configure_home_page()
    st.write('$~$')

    progress_bar = st.progress(0, text='Loading data from database...')
    db = init_db()
    with Session(db.engine) as session, session.begin():
        progress_bar.progress(25, text='Loading data from database...')
        minutes_since_last_update = db.calc_minutes_since_last_update(
            session, FlightSamples.sample_entry_date_utc)
        progress_bar.progress(50, text='Loading data from database...')
        total_flights_rows = db.count_total_rows(session, FlightSamples)
        progress_bar.progress(75, text='Loading data from database...')
        count_flights_samples = db.count_distinct(session, FlightSamples.sample_entry_date_utc)
        progress_bar.progress(100, text='Loading data from database...')
    progress_bar.empty()
    
    st.subheader(f'Last Database Update: `{minutes_since_last_update}` minutes ago')
    st.subheader(f'`{total_flights_rows}` data points stored from `{count_flights_samples}` samples'
                 + ' of real-time flights in the continental US')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
