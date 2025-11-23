from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date
from uuid import UUID
from app.models.membership import DurationType, MembershipStatus


# Membership Plan Schemas
class MembershipPlanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    duration_days: int = Field(..., gt=0)
    duration_type: DurationType
    setup_fee: float = Field(default=0, ge=0)
    features: Dict[str, Any] = Field(default_factory=dict)
    access_hours: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class MembershipPlanCreate(MembershipPlanBase):
    pass


class MembershipPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    duration_days: Optional[int] = Field(None, gt=0)
    duration_type: Optional[DurationType] = None
    setup_fee: Optional[float] = Field(None, ge=0)
    features: Optional[Dict[str, Any]] = None
    access_hours: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MembershipPlanResponse(MembershipPlanBase):
    id: UUID
    organization_id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# Membership Schemas
class MembershipBase(BaseModel):
    plan_id: UUID
    start_date: date
    end_date: date
    auto_renew: bool = True


class MembershipCreate(MembershipBase):
    member_id: UUID


class MembershipUpdate(BaseModel):
    plan_id: Optional[UUID] = None
    end_date: Optional[date] = None
    auto_renew: Optional[bool] = None
    status: Optional[MembershipStatus] = None


class MembershipFreeze(BaseModel):
    freeze_start_date: date
    freeze_end_date: date


class MembershipCancel(BaseModel):
    cancellation_reason: Optional[str] = Field(None, max_length=500)


class MembershipResponse(MembershipBase):
    id: UUID
    organization_id: UUID
    member_id: UUID
    status: MembershipStatus
    freeze_start_date: Optional[date] = None
    freeze_end_date: Optional[date] = None
    cancellation_date: Optional[date] = None
    cancellation_reason: Optional[str] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
