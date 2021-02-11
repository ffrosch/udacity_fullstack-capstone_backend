from datetime import datetime

from sqlalchemy import func, ForeignKey, Column, Date, Integer, String, Time
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from app import db


class Tour(db.Model):
    """A tour/trip, including its geospatial data."""

    __tablename__ = 'tours'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'))
    name = Column(String, nullable=False)
    description = Column(String)
    date = Column(Date, nullable=False)
    starttime = Column(Time)
    endtime = Column(Time)
    accesslevel_id = Column(Integer, ForeignKey('accesslevels.id'))
    location = Column(Geometry(geometry_type="POINT",
                               srid=4326), nullable=False)

    def __repr__(self):
        return f'<{self.name}, {self.date}, {self.geo_text}>'

    @property
    def geo_srid(self):
        srid = db.session.scalar(self.location.ST_SRID())
        return srid

    @property
    def geo_text(self):
        txt = db.session.scalar(self.location.ST_AsText())
        return txt

    @property
    def XY(self):
        X = db.session.scalar(self.location.ST_X())
        Y = db.session.scalar(self.location.ST_Y())
        return X, Y

    def as_geojson(self):
        # TODO: Add all class attributes to the output
        geo = db.session.scalar(self.location.ST_AsGeoJSON())
        return geo

    def as_shape(self):
        # TODO: For future use
        return to_shape(self.location)


class Activity(db.Model):
    """An outdoor activity."""

    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    tours = relationship("Tour", cascade="all, delete-orphan")


class Accesslevel(db.Model):
    """Access levels define who has access to an entry.

    Levels:
    - Public
    (- Friend) -> Future Release
    - Private"""

    __tablename__ = 'accesslevels'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tours = relationship("Tour", cascade="all, delete-orphan")
