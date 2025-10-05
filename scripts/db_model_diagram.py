from database.models import (
    FlightSamples, RecentFlightSamples, RandomFlightSamples, FlightEmergencies, FlightAggregates,
    DailyFlightTotals, WeeklyFlightTotals, MonthlyFlightTotals, DailyTopAircraft, WeeklyTopAircraft,
    MonthlyTopAircraft, MonthlyTopFlights
)

from sqlalchemy.orm import relationship
import sqlalchemy_data_model_visualizer as sql_dmv

import os


output_file_name = 'src/skyviz/static/db_model_diagram'
svg_file_name = f'{output_file_name}.svg'

models = [
    FlightSamples,
    RecentFlightSamples,
    RandomFlightSamples,
    FlightEmergencies,
    FlightAggregates,
    DailyFlightTotals,
    WeeklyFlightTotals,
    MonthlyFlightTotals,
    DailyTopAircraft,
    WeeklyTopAircraft,
    MonthlyTopAircraft,
    MonthlyTopFlights,
]

# Sampling Layer
FlightSamples.recent_entries = relationship(
    RecentFlightSamples,
    primaryjoin=RecentFlightSamples.icao_id == FlightSamples.icao_id,
    foreign_keys=[RecentFlightSamples.icao_id]
)
FlightSamples.sample = relationship(
    RandomFlightSamples,
    primaryjoin=RandomFlightSamples.icao_id == FlightSamples.icao_id,
    foreign_keys=[RandomFlightSamples.icao_id]
)
FlightSamples.emergencies = relationship(
    FlightEmergencies,
    primaryjoin=FlightEmergencies.icao_id == FlightSamples.icao_id,
    foreign_keys=[FlightEmergencies.icao_id]
)


# Analysis Layer
FlightSamples.aggregate = relationship(
    FlightAggregates,
    primaryjoin=FlightAggregates.sample_entry_date_utc == FlightSamples.sample_entry_date_utc,
    foreign_keys=[FlightAggregates.sample_entry_date_utc]
)
FlightSamples.daily_unique_aircraft = relationship(
    DailyTopAircraft,
    primaryjoin=DailyTopAircraft.sample_date == FlightSamples.sample_entry_date_utc,
    foreign_keys=[DailyTopAircraft.sample_date]
)
# WeeklyTopAircraft
FlightSamples.weekly_unique_aircraft = relationship(
    WeeklyTopAircraft,
    primaryjoin=WeeklyTopAircraft.week_start_date == FlightSamples.sample_entry_date_utc,
    foreign_keys=[WeeklyTopAircraft.week_start_date]
)
DailyTopAircraft.num_of_flights = relationship(
    WeeklyTopAircraft,
    primaryjoin=WeeklyTopAircraft.week_start_date == DailyTopAircraft.sample_date,
    foreign_keys=[WeeklyTopAircraft.week_start_date],
    viewonly=True
)
# MonthlyTopAircraft
FlightSamples.monthly_unique_aircraft = relationship(
    MonthlyTopAircraft,
    primaryjoin=MonthlyTopAircraft.month_start_date == FlightSamples.sample_entry_date_utc,
    foreign_keys=[MonthlyTopAircraft.month_start_date]
)
WeeklyTopAircraft.num_of_flights = relationship(
    MonthlyTopAircraft,
    primaryjoin=MonthlyTopAircraft.month_start_date == WeeklyTopAircraft.week_start_date,
    foreign_keys=[MonthlyTopAircraft.month_start_date],
    viewonly=True
)
# MonthlyTopFlights
FlightSamples.monthly_unique_flights = relationship(
    MonthlyTopFlights,
    primaryjoin=MonthlyTopFlights.month_start_date == FlightSamples.sample_entry_date_utc,
    foreign_keys=[MonthlyTopFlights.month_start_date]
)


# Presentation Layer
FlightAggregates.daily_totals = relationship(
    DailyFlightTotals,
    primaryjoin=DailyFlightTotals.sample_date == FlightAggregates.sample_entry_date_utc,
    foreign_keys=[DailyFlightTotals.sample_date]
)
FlightAggregates.weekly_totals = relationship(
    WeeklyFlightTotals,
    primaryjoin=WeeklyFlightTotals.week_start_date == FlightAggregates.sample_entry_date_utc,
    foreign_keys=[WeeklyFlightTotals.week_start_date]
)
FlightAggregates.monthly_totals = relationship(
    MonthlyFlightTotals,
    primaryjoin=MonthlyFlightTotals.month_start_date == FlightAggregates.sample_entry_date_utc,
    foreign_keys=[MonthlyFlightTotals.month_start_date]
)


sql_dmv.generate_data_model_diagram(models, output_file_name, add_labels=False)
sql_dmv.add_web_font_and_interactivity(svg_file_name, svg_file_name)
os.remove(output_file_name)
