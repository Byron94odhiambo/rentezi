# app/models/maintenance.py
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class MaintenanceStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"

class MaintenancePriority(int, enum.Enum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1

class MaintenanceRequest(BaseModel):
    __tablename__ = "maintenance_requests"

    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM)
    resolved_at = Column(DateTime)

    # Relationships
    unit = relationship("Unit", back_populates="maintenance_requests")
    tenant = relationship("User", back_populates="maintenance_requests")