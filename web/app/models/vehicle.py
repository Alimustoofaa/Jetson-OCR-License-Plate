from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DATETIME, FLOAT, TIMESTAMP
from sqlalchemy.sql.traversals import COMPARE_FAILED

from ..config.database import Base


class Vehicle(Base):
    __tablename__ = "tb_vehicle"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DATETIME)
    license_plate = Column(String)
    conf_license_plate = Column(FLOAT)
    vehicle_type = Column(String)
    conf_vehicle_type = Column(FLOAT)
    processing_time = Column(FLOAT)
    image_filename = Column(String)
