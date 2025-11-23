from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from app.models.equipment import EquipmentStatus


# Equipment Schemas
class EquipmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    purchase_date: date
    warranty_expiry: Optional[date] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    warranty_expiry: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None


class EquipmentResponse(EquipmentBase):
    id: UUID
    organization_id: UUID
    status: EquipmentStatus
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Maintenance Log
class MaintenanceLog(BaseModel):
    equipment_id: UUID
    maintenance_date: date
    description: str = Field(..., max_length=1000)
    cost: Optional[float] = Field(None, ge=0)
    performed_by: str = Field(..., max_length=100)
    next_maintenance_date: Optional[date] = None
