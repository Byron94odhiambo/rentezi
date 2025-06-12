from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from ..models.user import User, UserRole
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id_number(db: Session, id_number: str) -> Optional[User]:
    return db.query(User).filter(User.id_number == id_number).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        id_number=user.id_number,
        hashed_password=hashed_password,
        role=user.role,
        is_verified=True  # Skip verification for MVP
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_users_by_role(db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()