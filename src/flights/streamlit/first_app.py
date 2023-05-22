import streamlit as st
import numpy as np
import pandas as pd
import time

from flights.streamlit.sections.sidebar import sidebar

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

st.title('Flight Data')

with st.sidebar:
    sidebar()

left_column, right_column = st.columns(2)

with left_column:
    x = st.slider('multiplier', value=1)

    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

    st.line_chart(chart_data.multiply(x))

    map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
        columns=['lat', 'lon'])

    st.map(map_data)

with right_column:
    if st.checkbox('Show dataframe'):
        chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])
        chart_data


    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
        })

    option = st.selectbox(
        'Which number do you like best?',
        df['first column'])

    'You selected: ', option

with st.expander('Expand'):
    st.write('This text is hidden')
    latest_iteration = st.empty()
    bar = st.progress(0)

    for i in range(100):
        # Update the progress bar with each iteration.
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.1)
