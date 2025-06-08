from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PropertyBase(BaseModel):
    name: str
    address: str
    city: str
    county: str
    description: Optional[str] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int
    landlord_id: int
    created_at: datetime
    units_count: Optional[int] = 0
    occupied_units: Optional[int] = 0
    
    class Config:
        from_attributes = True

# For compatibility
Property = PropertyResponse
