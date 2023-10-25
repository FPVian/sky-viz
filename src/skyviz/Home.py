from skyviz.sections.page_configs import configure_home_page
from skyviz.data.cached_functions import Cache
from skyviz.utils import logger
from database.models import FlightSamples, FlightAggregates

import streamlit as st
import polars as pl
import altair as alt
import pydeck as pdk

log = logger.create(__name__)

# Streamlit API reference: https://docs.streamlit.io/library/api-reference
# Altair API reference: https://altair-viz.github.io/user_guide/api.html
# Pydeck docs: https://deckgl.readthedocs.io/en/latest/
# Plotly figures: https://plotly.com/python/reference/index/
# Plotly API Reference: https://plotly.com/python-api-reference/


def main():
    configure_home_page()
    st.write('$~$')
    flight_aggregates: pl.DataFrame = Cache.read_table(FlightAggregates)


    col1, col2, col3, col4, col5 = st.columns(5)  # row of metrics
    col1.metric('Total Flights',  # change total flights to sum monthly aggregates (cur. # data points)
                flight_aggregates.select(pl.col(FlightAggregates.number_of_flights.name).sum()).item())
    col2.metric('Current Aircraft', Cache.get_current_flights_count(), Cache.calc_change_in_flights())
    col3.metric('Max Aircraft',
                flight_aggregates.select(pl.col(FlightAggregates.number_of_flights.name).max()))
    col4.metric('Average Aircraft',
                round(flight_aggregates.select(pl.col(FlightAggregates.number_of_flights.name).mean()).item(),1))
    col5.metric('Min Aircraft',
            flight_aggregates.select(pl.col(FlightAggregates.number_of_flights.name).min()))


    left_column, right_column = st.columns(2)
    with left_column:
        st.altair_chart(  # flights over time line graph
            alt.Chart(
                Cache.filter_flight_aggregates_by_recent_days(num_days := 3),
                title=f'Airborne Flights, last {num_days} days',
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


        st.pydeck_chart(pdk.Deck(  # flight routes by altitude
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=34,
                longitude=-98,
                zoom=4,
                pitch=45,
            ),
            layers=[
                pdk.Layer(
                'HexagonLayer',
                data=Cache.read_latest_flight_sample(),
                get_position=[FlightSamples.longitude.name, FlightSamples.latitude.name],
                radius=10000,
                elevation_scale=4,
                elevation_range=[0, 100000],
                pickable=True,
                extruded=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=Cache.read_latest_flight_sample(),
                    get_position=[FlightSamples.longitude.name, FlightSamples.latitude.name],
                    get_color='[200, 30, 0, 160]',
                    get_radius=10000,
                ),
            ],
        ))


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


        st.pydeck_chart(pdk.Deck(  # flight routes by altitude
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=34,
                longitude=-98,
                zoom=4,
                pitch=45,
            ),
            layers=[
                pdk.Layer(
                'HexagonLayer',
                data=Cache.read_latest_flight_sample(),
                get_position=[FlightSamples.longitude.name, FlightSamples.latitude.name],
                radius=10000,
                elevation_scale=4,
                elevation_range=[0, 100000],
                pickable=True,
                extruded=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=Cache.read_latest_flight_sample(),
                    get_position=[FlightSamples.longitude.name, FlightSamples.latitude.name],
                    get_color='[200, 30, 0, 160]',
                    get_radius=10000,
                ),
            ],
        ))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
