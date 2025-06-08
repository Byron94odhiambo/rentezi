# app/models/payment.py
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"

class Payment(BaseModel):
    __tablename__ = "payments"

    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime)
    mpesa_reference = Column(String)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    for_month = Column(String, nullable=False)  # Format: "YYYY-MM"
    for_year = Column(Integer, nullable=False)
    notes = Column(String)

    # Relationships
    assignment = relationship("Assignment", back_populates="payments")
    tenant = relationship("User", back_populates="payments")