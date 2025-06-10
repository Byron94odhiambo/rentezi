# app/services/maintenance_service.py
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from ..models.maintenance import MaintenanceRequest, MaintenanceStatus
from ..models.unit import Unit
from ..models.property import Property
from ..models.user import User
from ..schemas.maintenance import MaintenanceRequestCreate

def create_maintenance_request(db: Session, request: MaintenanceRequestCreate, tenant_id: int) -> MaintenanceRequest:
    db_request = MaintenanceRequest(
        **request.dict(),
        tenant_id=tenant_id,
        status=MaintenanceStatus.PENDING
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_maintenance_request_by_id(db: Session, request_id: int) -> Optional[MaintenanceRequest]:
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()

def get_maintenance_requests_by_tenant(db: Session, tenant_id: int) -> List[MaintenanceRequest]:
    requests = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.tenant_id == tenant_id
    ).options(
        joinedload(MaintenanceRequest.unit).joinedload(Unit.property)
    ).all()
    
    # Add computed fields
    for request in requests:
        tenant = db.query(User).filter(User.id == request.tenant_id).first()
        request.tenant_name = f"{tenant.first_name} {tenant.last_name}"
        request.unit_info = f"{request.unit.unit_number}"
        request.property_name = request.unit.property.name
    
    return requests

def get_maintenance_requests_by_landlord(db: Session, landlord_id: int) -> List[MaintenanceRequest]:
    requests = db.query(MaintenanceRequest).join(Unit).join(Property).filter(
        Property.landlord_id == landlord_id
    ).options(
        joinedload(MaintenanceRequest.unit).joinedload(Unit.property),
        joinedload(MaintenanceRequest.tenant)
    ).all()
    
    # Add computed fields
    for request in requests:
        request.tenant_name = f"{request.tenant.first_name} {request.tenant.last_name}"
        request.unit_info = f"{request.unit.unit_number}"
        request.property_name = request.unit.property.name
    
    return requests

def update_maintenance_status(db: Session, request_id: int, status: MaintenanceStatus) -> Optional[MaintenanceRequest]:
    request = get_maintenance_request_by_id(db, request_id)
    if not request:
        return None
    
    request.status = status
    if status == MaintenanceStatus.COMPLETED:
        request.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(request)
    return request
