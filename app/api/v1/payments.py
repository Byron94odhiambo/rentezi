# app/api/v1/payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...models.payment import PaymentStatus
from ...schemas.payment import PaymentCreate, PaymentResponse
from ...services.payment_service import create_payment, get_payments_by_tenant, get_payments_by_landlord, update_payment_status
from ...services.assignment_service import get_assignment_by_id

router = APIRouter()

@router.post("/", response_model=PaymentResponse)
def record_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify assignment exists
    assignment = get_assignment_by_id(db, payment.assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # For MVP, allow both tenants and landlords to record payments
    if current_user.role == UserRole.TENANT and current_user.id != assignment.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to record payment for this assignment"
        )
    
    return create_payment(db, payment, assignment.tenant_id)

@router.get("/tenant/payments", response_model=List[PaymentResponse])
def get_tenant_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.TENANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenants can access this endpoint"
        )
    
    return get_payments_by_tenant(db, current_user.id, skip, limit)

@router.get("/landlord/payments", response_model=List[PaymentResponse])
def get_landlord_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only landlords and admins can access this endpoint"
        )
    
    return get_payments_by_landlord(db, current_user.id, skip, limit)

@router.put("/{payment_id}/status")
def update_payment_status_endpoint(
    payment_id: int,
    status: PaymentStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.LANDLORD, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only landlords and admins can update payment status"
        )
    
    payment = update_payment_status(db, payment_id, status)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return {"message": "Payment status updated successfully"}