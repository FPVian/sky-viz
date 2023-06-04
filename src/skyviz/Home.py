from skyviz.utils import logger
from skyviz.sections.sidebar import sidebar
from skyviz.utils.temp import DemoData

import streamlit as st

from datetime import timedelta

log = logger.create(__name__)

st.set_page_config(
    page_title='Flight Data',
    page_icon='✈️',
    layout='wide',
    menu_items={
        'Get help': 'mailto:ian@skyviz.app?subject=SkyViz%20Help',
        'About': '''
            ### Github
            [Source](https://www.github.com/fpvian/flight-data)

            [Creator's Profile](https://www.github.com/fpvian)

            ---
            ''',
        },
    )

st.title('Flight Data')


# @st.cache_resource
# def init_db_connection():
#     pass


@st.cache_data(ttl=timedelta(minutes=60))
def fetch_data():
    latitude = 39.8564  # Denver International Airport
    longitude = -104.6764  # Denver International Airport
    response = DemoData().get_aircraft_scatter(latitude, longitude)
    return response


data = fetch_data()


st.subheader('Map of current flights within 1,000km of Denver International Airport')
st.map(data)

with st.sidebar:
    sidebar()

# left_column, right_column = st.columns(2)

# with left_column:
#     pass

# with right_column:
#     pass


def main():
    pass


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log.error(e)
        raise e
