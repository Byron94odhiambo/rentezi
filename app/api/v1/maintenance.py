# app/api/v1/maintenance.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...models.maintenance import MaintenanceStatus
from ...schemas.maintenance import MaintenanceRequestCreate, MaintenanceRequestResponse
from ...services.maintenance_service import (
    create_maintenance_request, 
    get_maintenance_requests_by_tenant, 
    get_maintenance_requests_by_landlord,
    update_maintenance_status
)
from ...services.unit_service import get_unit_by_id
from ...services.property_service import get_property_by_id

router = APIRouter()

@router.post("/", response_model=MaintenanceRequestResponse)
def create_maintenance(
    request: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify unit exists
    unit = get_unit_by_id(db, request.unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check authorization (tenant must be assigned to unit or landlord must own property)
    if current_user.role == UserRole.TENANT:
        # Check if tenant is assigned to this unit
        from ...services.assignment_service import get_assignments_by_tenant
        tenant_assignments = get_assignments_by_tenant(db, current_user.id)
        if not any(assignment.unit_id == request.unit_id and assignment.is_active for assignment in tenant_assignments):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create maintenance request for this unit"
            )
    elif current_user.role == UserRole.LANDLORD:
        property = get_property_by_id(db, unit.property_id)
        if property.landlord_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create maintenance request for this unit"
            )
    
    return create_maintenance_request(db, request, current_user.id)

@router.get("/tenant/requests", response_model=List[MaintenanceRequestResponse])
def get_tenant_maintenance_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.TENANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenants can access this endpoint"
        )
    
    return get_maintenance_requests_by_tenant(db, current_user.id)

@router.get("/landlord/requests", response_model=List[MaintenanceRequestResponse])
def get_landlord_maintenance_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only landlords and admins can access this endpoint"
        )
    
    return get_maintenance_requests_by_landlord(db, current_user.id)

@router.put("/{request_id}/status")
def update_maintenance_request_status(
    request_id: int,
    status: MaintenanceStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only landlords and admins can update maintenance status"
        )
    
    request = update_maintenance_status(db, request_id, status)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    
    return {"message": "Maintenance request status updated successfully"}