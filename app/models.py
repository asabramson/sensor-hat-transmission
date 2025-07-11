from app import db
from datetime import datetime
from typing import Optional

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

class TrafficData(db.Model):
    __tablename__ = 'traffic_data'
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    device_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)   
    count : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)
    timestamp : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now())
    #timestamp  = db.Column(db.DateTime, default=datetime.now) TRADITIONAL IMPLEMENTATION


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    device_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)   
    temperature : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    humidity : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    pressure : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)
    timestamp : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now())