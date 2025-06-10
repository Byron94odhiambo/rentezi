from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from ..models.property import Property
from ..models.unit import Unit, UnitStatus
from ..schemas.property import PropertyCreate

def create_property(db: Session, property: PropertyCreate, landlord_id: int) -> Property:
    db_property = Property(
        **property.dict(),
        landlord_id=landlord_id
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property

def get_property_by_id(db: Session, property_id: int) -> Optional[Property]:
    return db.query(Property).filter(Property.id == property_id).first()

def get_properties_by_landlord(db: Session, landlord_id: int, skip: int = 0, limit: int = 100) -> List[Property]:
    return db.query(Property).filter(Property.landlord_id == landlord_id).offset(skip).limit(limit).all()

def get_property_with_stats(db: Session, property_id: int):
    property = get_property_by_id(db, property_id)
    if not property:
        return None
    
    # Get unit statistics
    units_count = db.query(func.count(Unit.id)).filter(Unit.property_id == property_id).scalar()
    occupied_units = db.query(func.count(Unit.id)).filter(
        Unit.property_id == property_id,
        Unit.status == UnitStatus.OCCUPIED
    ).scalar()
    
    # Add computed fields
    property.units_count = units_count or 0
    property.occupied_units = occupied_units or 0
    
    return property

def update_property(db: Session, property_id: int, property_update: dict) -> Optional[Property]:
    db_property = get_property_by_id(db, property_id)
    if not db_property:
        return None
    
    for key, value in property_update.items():
        setattr(db_property, key, value)
    
    db.commit()
    db.refresh(db_property)
    return db_property

def delete_property(db: Session, property_id: int) -> bool:
    db_property = get_property_by_id(db, property_id)
    if not db_property:
        return False
    
    db.delete(db_property)
    db.commit()
    return True