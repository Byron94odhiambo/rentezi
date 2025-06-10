# app/services/assignment_service.py
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date
from ..models.assignment import Assignment
from ..models.unit import Unit, UnitStatus
from ..models.user import User
from ..models.property import Property
from ..schemas.assignment import AssignmentCreate

def create_assignment(db: Session, assignment: AssignmentCreate, unit_id: int) -> Assignment:
    # Check if unit is available
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise ValueError("Unit not found")
    
    # Deactivate any existing assignments for this unit
    existing_assignment = db.query(Assignment).filter(
        Assignment.unit_id == unit_id,
        Assignment.is_active == True
    ).first()
    
    if existing_assignment:
        existing_assignment.is_active = False
        db.commit()
    
    # Create new assignment
    db_assignment = Assignment(
        unit_id=unit_id,
        **assignment.dict(),
        is_active=True
    )
    db.add(db_assignment)
    
    # Update unit status
    unit.status = UnitStatus.OCCUPIED
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_assignment_by_id(db: Session, assignment_id: int) -> Optional[Assignment]:
    return db.query(Assignment).filter(Assignment.id == assignment_id).first()

def get_assignments_by_tenant(db: Session, tenant_id: int) -> List[Assignment]:
    assignments = db.query(Assignment).filter(
        Assignment.tenant_id == tenant_id
    ).options(
        joinedload(Assignment.unit).joinedload(Unit.property)
    ).all()
    
    # Add computed fields
    for assignment in assignments:
        tenant = db.query(User).filter(User.id == assignment.tenant_id).first()
        assignment.tenant_name = f"{tenant.first_name} {tenant.last_name}" if tenant else None
        assignment.unit_info = f"{assignment.unit.unit_number}"
        assignment.property_name = assignment.unit.property.name
    
    return assignments

def get_assignments_by_landlord(db: Session, landlord_id: int) -> List[Assignment]:
    assignments = db.query(Assignment).join(Unit).join(Property).filter(
        Property.landlord_id == landlord_id
    ).options(
        joinedload(Assignment.unit).joinedload(Unit.property),
        joinedload(Assignment.tenant)
    ).all()
    
    # Add computed fields
    for assignment in assignments:
        assignment.tenant_name = f"{assignment.tenant.first_name} {assignment.tenant.last_name}"
        assignment.unit_info = f"{assignment.unit.unit_number}"
        assignment.property_name = assignment.unit.property.name
    
    return assignments

def end_assignment(db: Session, assignment_id: int) -> Optional[Assignment]:
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        return None
    
    assignment.is_active = False
    
    # Update unit status to vacant
    unit = db.query(Unit).filter(Unit.id == assignment.unit_id).first()
    if unit:
        unit.status = UnitStatus.VACANT
    
    db.commit()
    db.refresh(assignment)
    return assignment