# app/api/v1/assignments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...schemas.assignment import AssignmentCreate, AssignmentResponse
from ...services.assignment_service import create_assignment, get_assignments_by_tenant, get_assignments_by_landlord
from ...services.unit_service import get_unit_by_id
from ...services.property_service import get_property_by_id

router = APIRouter()

@router.post("/units/{unit_id}/assign", response_model=AssignmentResponse)
def assign_tenant_to_unit(
    unit_id: int,
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign units"
        )
    
    # Check if unit exists
    unit = get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if landlord owns the property
    if current_user.role == UserRole.LANDLORD:
        property = get_property_by_id(db, unit.property_id)
        if property.landlord_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to assign this unit"
            )
    
    try:
        return create_assignment(db, assignment, unit_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/tenant/assignments", response_model=List[AssignmentResponse])
def get_tenant_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.TENANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenants can access this endpoint"
        )
    
    return get_assignments_by_tenant(db, current_user.id)

@router.get("/landlord/assignments", response_model=List[AssignmentResponse])
def get_landlord_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only landlords and admins can access this endpoint"
        )
    
    return get_assignments_by_landlord(db, current_user.id)