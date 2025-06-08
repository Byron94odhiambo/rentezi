from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class UserRole(str, enum.Enum):
    TENANT = "tenant"
    LANDLORD = "landlord"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
    id_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Relationships
    properties = relationship("Property", back_populates="landlord")
    tenant_assignments = relationship("Assignment", back_populates="tenant")
    payments = relationship("Payment", back_populates="tenant")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")