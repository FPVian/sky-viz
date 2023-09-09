from skyviz.config.settings import s
from skyviz.utils import logger
from database.models import Base
from skyviz.db.base_repo import BaseRepository

import streamlit as st
import pandas as pd
from hydra.utils import instantiate

from datetime import timedelta

log = logger.create(__name__)

'''
These functions make use of the db repository but must remain separate since the results are cached.
'''


@st.cache_resource
def init_db() -> BaseRepository:
    log.info('caching database connection')
    return instantiate(s.db)


@st.cache_data(ttl=timedelta(minutes=s.general.cache_time_to_live_min))
def read_table(table_model: Base) -> pd.DataFrame:
    '''
    Reads an entire table into a pandas dataframe. Will be used for OLAP.
    '''
    log.info(f'caching {table_model.__tablename__} table')
    db = init_db()
    table = pd.read_sql_table(table_model.__tablename__, db.engine)
    return table
