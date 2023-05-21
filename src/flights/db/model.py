from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.types import DateTime

'''
See the docs for SQLAlchemy annotated declarative tables here:
https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-annotated-declarative-table-type-annotated-forms-for-mapped-column

And writing SQL statements here:
https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
'''


class Base(DeclarativeBase):
    pass


class Flights(Base):
    __tablename__ = 'flights'

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_date_utc: Mapped[DateTime]
    latitude: Mapped[float]
    longitude: Mapped[float]
    number_of_flights: Mapped[int]
