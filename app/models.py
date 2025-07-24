from app import db
from datetime import datetime
from typing import Optional

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

# NOT ACTUALLY USED IN SIMULATION
# Left in code to demonstrate what the real world model would look like
class TrafficData(db.Model):
    __tablename__ = 'traffic_data'
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    location_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)   
    in_count : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)
    out_count : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)
    timestamp : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    # Real world implementation would likely use exact timestamps, for the simulation, we will use a counter to increment in 15 second intervals
    # timestamp : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now())


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    device_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)   
    temperature : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    humidity : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    pressure : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    timestamp : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now())