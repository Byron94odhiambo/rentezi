from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.maintenance import MaintenanceStatus, MaintenancePriority

class MaintenanceRequestBase(BaseModel):
    issue_type: str
    description: str
    priority: MaintenancePriority = MaintenancePriority.MEDIUM

class MaintenanceRequestCreate(MaintenanceRequestBase):
    unit_id: int

class MaintenanceRequestResponse(MaintenanceRequestBase):
    id: int
    unit_id: int
    tenant_id: int
    status: MaintenanceStatus
    resolved_at: Optional[datetime] = None
    created_at: datetime
    tenant_name: Optional[str] = None
    unit_info: Optional[str] = None
    property_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# For compatibility
MaintenanceRequest = MaintenanceRequestResponse
