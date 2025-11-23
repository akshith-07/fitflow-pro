from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.lead import LeadStatus, LeadSource


# Lead Schemas
class LeadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=1, max_length=20)
    source: LeadSource
    notes: Optional[str] = Field(None, max_length=2000)


class LeadCreate(LeadBase):
    assigned_to: Optional[UUID] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    id: UUID
    organization_id: UUID
    status: LeadStatus
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadConvert(BaseModel):
    membership_plan_id: UUID
    start_date: date

    from datetime import date
