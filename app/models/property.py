from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Property(BaseModel):
    __tablename__ = "properties"

    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    county = Column(String, nullable=False)
    description = Column(Text)
    landlord_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    landlord = relationship("User", back_populates="properties")
    units = relationship("Unit", back_populates="property", cascade="all, delete-orphan")