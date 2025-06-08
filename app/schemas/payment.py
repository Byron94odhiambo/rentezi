from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.payment import PaymentStatus

class PaymentBase(BaseModel):
    amount: float
    for_month: str  # Format: "YYYY-MM"
    for_year: int
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    assignment_id: int
    mpesa_reference: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    assignment_id: int
    tenant_id: int
    payment_date: Optional[datetime] = None
    mpesa_reference: Optional[str] = None
    status: PaymentStatus
    created_at: datetime
    tenant_name: Optional[str] = None
    unit_info: Optional[str] = None
    
    class Config:
        from_attributes = True

# For compatibility
Payment = PaymentResponse
