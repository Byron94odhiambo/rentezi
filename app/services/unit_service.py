from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..models.unit import Unit, UnitStatus
from ..models.assignment import Assignment
from ..models.user import User
from ..schemas.unit import UnitCreate

def create_unit(db: Session, unit: UnitCreate, property_id: int) -> Unit:
    db_unit = Unit(
        **unit.dict(),
        property_id=property_id
    )
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

def get_unit_by_id(db: Session, unit_id: int) -> Optional[Unit]:
    return db.query(Unit).filter(Unit.id == unit_id).first()

def get_units_by_property(db: Session, property_id: int) -> List[Unit]:
    units = db.query(Unit).filter(Unit.property_id == property_id).all()
    
    # Add current tenant info
    for unit in units:
        active_assignment = db.query(Assignment).filter(
            Assignment.unit_id == unit.id,
            Assignment.is_active == True
        ).first()
        
        if active_assignment:
            tenant = db.query(User).filter(User.id == active_assignment.tenant_id).first()
            unit.current_tenant = f"{tenant.first_name} {tenant.last_name}" if tenant else None
        else:
            unit.current_tenant = None
    
    return units

def update_unit_status(db: Session, unit_id: int, status: UnitStatus) -> Optional[Unit]:
    db_unit = get_unit_by_id(db, unit_id)
    if not db_unit:
        return None
    
    db_unit.status = status
    db.commit()
    db.refresh(db_unit)
    return db_unit

def get_vacant_units(db: Session, property_id: Optional[int] = None) -> List[Unit]:
    query = db.query(Unit).filter(Unit.status == UnitStatus.VACANT)
    if property_id:
        query = query.filter(Unit.property_id == property_id)
    return query.all()