# app/services/payment_service.py
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from ..models.payment import Payment, PaymentStatus
from ..models.assignment import Assignment
from ..models.unit import Unit
from ..models.property import Property
from ..models.user import User
from ..schemas.payment import PaymentCreate

def create_payment(db: Session, payment: PaymentCreate, tenant_id: int) -> Payment:
    db_payment = Payment(
        **payment.dict(),
        tenant_id=tenant_id,
        payment_date=datetime.utcnow(),
        status=PaymentStatus.PAID
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_payments_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
    payments = db.query(Payment).filter(
        Payment.tenant_id == tenant_id
    ).options(
        joinedload(Payment.assignment).joinedload(Assignment.unit).joinedload(Unit.property)
    ).offset(skip).limit(limit).all()
    
    # Add computed fields
    for payment in payments:
        tenant = db.query(User).filter(User.id == payment.tenant_id).first()
        payment.tenant_name = f"{tenant.first_name} {tenant.last_name}"
        payment.unit_info = f"{payment.assignment.unit.unit_number}"
    
    return payments

def get_payments_by_landlord(db: Session, landlord_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
    payments = db.query(Payment).join(Assignment).join(Unit).join(Property).filter(
        Property.landlord_id == landlord_id
    ).options(
        joinedload(Payment.assignment).joinedload(Assignment.unit).joinedload(Unit.property),
        joinedload(Payment.tenant)
    ).offset(skip).limit(limit).all()
    
    # Add computed fields
    for payment in payments:
        payment.tenant_name = f"{payment.tenant.first_name} {payment.tenant.last_name}"
        payment.unit_info = f"{payment.assignment.unit.unit_number}"
    
    return payments

def update_payment_status(db: Session, payment_id: int, status: PaymentStatus) -> Optional[Payment]:
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        return None
    
    payment.status = status
    if status == PaymentStatus.PAID and not payment.payment_date:
        payment.payment_date = datetime.utcnow()
    
    db.commit()
    db.refresh(payment)
    return payment