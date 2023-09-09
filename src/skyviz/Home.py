from skyviz.sections.page_configs import configure_home_page
# from skyviz.sections.sidebar import sidebar
from skyviz.data.cached_functions import init_db
from skyviz.utils import logger
from database.models import FlightSamples

import streamlit as st
from sqlalchemy.orm import Session

log = logger.create(__name__)


def main():
    configure_home_page()
    st.write('$~$')

    db = init_db()
    with Session(db.engine) as session, session.begin():
        minutes_since_last_update = db.calc_minutes_since_last_update(
            session, FlightSamples.sample_entry_date_utc)
        total_flights_rows = db.count_total_rows(session, FlightSamples)
        count_flights_samples = db.count_distinct(session, FlightSamples.sample_entry_date_utc)
    
    st.subheader(f'Last Database Update: `{minutes_since_last_update}` minutes ago')
    st.subheader(f'`{total_flights_rows}` data points stored from `{count_flights_samples}` samples'
                 + ' of real-time flights in the continental US')


    # with st.sidebar:
    #     sidebar()

    # left_column, right_column = st.columns(2)

    # with left_column:
    #     st.write('this is a left column')

    # with right_column:
    #     st.write('this is a right column')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
