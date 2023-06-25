from skyviz.sections.page_configs import configure_home_page
# from skyviz.sections.sidebar import sidebar
from skyviz.data.cached_functions import read_table
from skyviz.utils import logger
from database.models import FlightSamples

import streamlit as st

log = logger.create(__name__)


def main():
    configure_home_page()

    flight_samples_data = read_table(FlightSamples)
    st.subheader('Recent Flights in the Continental US')
    st.map(flight_samples_data)

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
