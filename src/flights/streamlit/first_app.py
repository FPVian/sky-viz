import streamlit as st
import numpy as np
import pandas as pd
from datetime import timedelta

st.set_page_config(
    page_title='Flight Data',
    page_icon='✈️',
    layout='wide',
    menu_items={
        'Get help': 'mailto:distantdollars@gmail.com?subject=Flight%20Data%20Help',
        'About': '''
            ### Github
            [Source](https://www.github.com/fpvian/flight-data)

            [Creator's Profile](https://www.github.com/fpvian)

            ---
            ''',
        },
    )

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data(ttl=timedelta(minutes=60))
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Load 10,000 rows of data into the dataframe.
data = load_data(10000)


if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)


hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)