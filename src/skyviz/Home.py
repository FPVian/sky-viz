from skyviz.sections.page_configs import configure_home_page
from skyviz.data.cached_functions import init_db, read_table
from skyviz.utils import logger
from database.models import FlightAggregates

import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
import pytz

log = logger.create(__name__)

# Streamlit API reference: https://docs.streamlit.io/library/api-reference

time_zone = 'America/Chicago'

def main():
    configure_home_page()
    st.write('$~$')


    # load data from database
    progress_bar = st.progress(0, text='Loading data from database...')
    db = init_db()
    with Session(db.engine) as session, session.begin():
        progress_bar.progress(25, text='Loading data from database...')
        minutes_since_last_update = db.calc_minutes_since_last_update(
            session, FlightAggregates.sample_entry_date_utc)
        progress_bar.progress(50, text='Loading data from database...')
        flight_aggregates: pd.DataFrame = read_table(FlightAggregates)
        progress_bar.progress(75, text='Loading data from database...')
        count_flights_samples = db.count_total_rows(session, FlightAggregates)
        progress_bar.progress(100, text='Loading data from database...')
    progress_bar.empty()


    # calculations
    with st.spinner('Calculating...'):
        total_flights: int = flight_aggregates['number_of_flights'].sum()

        # convert dates to central time
        entry_date_col: str = FlightAggregates.sample_entry_date_utc.name
        num_flights_col: str = FlightAggregates.number_of_flights.name
        flight_aggregates[entry_date_col] = pd.to_datetime(flight_aggregates[entry_date_col], utc=True)
        flight_aggregates.set_index(entry_date_col)
        flight_aggregates[entry_date_col] = flight_aggregates[entry_date_col].dt.tz_convert(tz=time_zone)


    # dashboard
    left_column, right_column = st.columns(2)

    ## totals
    st.subheader(f'Last Database Update: `{minutes_since_last_update}` minutes ago')
    st.subheader(f'`{total_flights}` data points stored from `{count_flights_samples}` samples'
                 + ' of real-time flights in the continental US')

    with left_column:
        ## recent flight counts line graph
        start_time = datetime.now(tz=pytz.timezone(time_zone)) - timedelta(days=3)
        flight_count_vs_time = (
            alt.Chart(
                flight_aggregates[flight_aggregates[entry_date_col] > start_time],
                title='Airborne Flights, last 3 days',
            )
            .mark_line()
            .encode(
                x=alt.X(entry_date_col, title='Central Time'),
                y=alt.Y(num_flights_col, title=None),
                )
            .configure_title(anchor='middle')
        )
        st.altair_chart(flight_count_vs_time, use_container_width=True)

    with right_column:
        ## flight average daily bar graph
        start_time = datetime.now(tz=pytz.timezone(time_zone)) - timedelta(days=7)
        flight_count_trend = (
            alt.Chart(
                flight_aggregates[flight_aggregates[entry_date_col] > start_time],
                title='Average Flights per Day',
            )
            .mark_bar()
            .encode(
                x=alt.X(entry_date_col, title=None),
                y=alt.Y(num_flights_col, title=None),
                )
            .configure_title(anchor='middle')
        )
        st.altair_chart(flight_count_trend, use_container_width=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
