from skyviz.sections.page_configs import configure_home_page
from skyviz.data.cached_functions import Cache
from skyviz.utils import logger
from database.models import FlightAggregates

import streamlit as st
import polars as pl
import altair as alt

log = logger.create(__name__)

# Streamlit API reference: https://docs.streamlit.io/library/api-reference


def main():
    configure_home_page()
    st.write('$~$')
    flight_aggregates: pl.DataFrame = Cache.read_table(FlightAggregates)


    left_column, right_column = st.columns(2)
    with left_column:
        st.altair_chart(  # flights over time line graph
            alt.Chart(
                Cache.filter_flight_aggregates_by_recent_days(3),
                title='Airborne Flights, last 3 days',
            )
            .mark_area()
            .encode(
                x=alt.X(
                    field='sample_entry_date_ct',
                    title='Central Time',
                    type='temporal',
                    ),
                y=alt.Y(
                    FlightAggregates.number_of_flights.name,
                    title='Aircraft Count',
                    type='quantitative',
                    ),
                )
            .configure_title(anchor='middle'),
            use_container_width=True,
        )


    with right_column:
        st.altair_chart(  # total daily flights bar chart
            alt.Chart(
                Cache.filter_flight_aggregates_by_recent_days(7),
                title='Total Daily Flights',
            )
            .mark_bar()
            .encode(
                x=alt.X(
                    field='sample_entry_date_ct',
                    title='Date',
                    type='temporal',
                    timeUnit='date',
                    ),
                y=alt.Y(
                    FlightAggregates.number_of_flights.name,
                    title='Flight Count',
                    type='quantitative',
                    ),
                )
            .configure_title(anchor='middle'),
            use_container_width=True,
        )


    total_flights = flight_aggregates.select(pl.col(
        FlightAggregates.number_of_flights.name).sum()).item()
    count_flights_samples = flight_aggregates.select(pl.count()).item()
    st.subheader(f'`{total_flights}` data points stored from `{count_flights_samples}` samples'
                + ' of real-time flights')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
