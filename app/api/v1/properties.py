# app/api/v1/properties.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...schemas.property import PropertyCreate, PropertyResponse
from ...services.property_service import create_property, get_properties_by_landlord, get_property_with_stats

router = APIRouter()

@router.post("/", response_model=PropertyResponse)
def create_new_property(
    property: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create properties"
        )
    
    return create_property(db, property, current_user.id)

@router.get("/", response_model=List[PropertyResponse])
def get_properties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view properties"
        )
    
    properties = get_properties_by_landlord(db, current_user.id, skip, limit)
    
    # Add statistics to each property
    for property in properties:
        property_with_stats = get_property_with_stats(db, property.id)
        property.units_count = property_with_stats.units_count
        property.occupied_units = property_with_stats.occupied_units
    
    return properties

@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    property = get_property_with_stats(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.LANDLORD and property.landlord_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this property"
        )
    
    return property