import streamlit as st


def sidebar():
    # Add a selectbox to the sidebar:
    add_selectbox = st.selectbox(
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone')
    )

    # Add a slider to the sidebar:
    add_slider = st.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )
