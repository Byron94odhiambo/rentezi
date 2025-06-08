from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.unit import UnitStatus

class UnitBase(BaseModel):
    unit_number: str
    floor: Optional[str] = None
    bedrooms: int
    bathrooms: float
    square_feet: Optional[int] = None
    monthly_rent: float

class UnitCreate(UnitBase):
    pass

class UnitResponse(UnitBase):
    id: int
    property_id: int
    status: UnitStatus
    created_at: datetime
    current_tenant: Optional[str] = None
    
    class Config:
        from_attributes = True

# For compatibility
Unit = UnitResponse
