# app/api/v1/units.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...schemas.unit import UnitCreate, UnitResponse
from ...services.unit_service import create_unit, get_units_by_property, get_unit_by_id
from ...services.property_service import get_property_by_id

router = APIRouter()

@router.post("/properties/{property_id}/units/", response_model=UnitResponse)
def create_new_unit(
    property_id: int,
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if property exists and user owns it
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if current_user.role == UserRole.LANDLORD and property.landlord_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add units to this property"
        )
    
    return create_unit(db, unit, property_id)

@router.get("/properties/{property_id}/units/", response_model=List[UnitResponse])
def get_property_units(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if property exists and user has access
    property = get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if current_user.role == UserRole.LANDLORD and property.landlord_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view units in this property"
        )
    
    return get_units_by_property(db, property_id)

@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unit = get_unit_by_id(db, unit_id)
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.LANDLORD:
        property = get_property_by_id(db, unit.property_id)
        if property.landlord_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this unit"
            )
    
    return unit