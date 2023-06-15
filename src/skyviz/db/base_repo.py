from sqlalchemy import Engine

'''
See the docs for writing SQL statements with SQLAlchemy 2.0 here:
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html

Unit of work pattern: https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html

Pandas docs for reading SQL tables: https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html
'''


class BaseRepository():
    '''
    Base class for database interfaces.
    '''
    def __init__(self, engine: Engine):
        self.engine = engine
