# app/models/assignment.py
from sqlalchemy import Column, Integer, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Assignment(BaseModel):
    __tablename__ = "assignments"

    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    security_deposit = Column(Float, nullable=False)
    payment_due_day = Column(Integer, nullable=False)  # Day of month
    is_active = Column(Boolean, default=True)

    # Relationships
    unit = relationship("Unit", back_populates="assignments")
    tenant = relationship("User", back_populates="tenant_assignments")
    payments = relationship("Payment", back_populates="assignment")