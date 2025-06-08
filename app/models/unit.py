# app/models/unit.py
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class UnitStatus(str, enum.Enum):
    VACANT = "vacant"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

class Unit(BaseModel):
    __tablename__ = "units"

    unit_number = Column(String, nullable=False)
    floor = Column(String)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Float, nullable=False)
    square_feet = Column(Integer)
    monthly_rent = Column(Float, nullable=False)
    status = Column(Enum(UnitStatus), default=UnitStatus.VACANT)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    # Relationships
    property = relationship("Property", back_populates="units")
    assignments = relationship("Assignment", back_populates="unit")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="unit")