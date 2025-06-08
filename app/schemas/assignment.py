from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional

class AssignmentBase(BaseModel):
    start_date: date
    end_date: date
    monthly_rent: float
    security_deposit: float
    payment_due_day: int
    
    @validator('payment_due_day')
    def validate_payment_due_day(cls, v):
        if v < 1 or v > 31:
            raise ValueError('Payment due day must be between 1 and 31')
        return v

class AssignmentCreate(AssignmentBase):
    tenant_id: int

class AssignmentResponse(AssignmentBase):
    id: int
    unit_id: int
    tenant_id: int
    is_active: bool
    created_at: datetime
    tenant_name: Optional[str] = None
    unit_info: Optional[str] = None
    property_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# For compatibility
Assignment = AssignmentResponse
