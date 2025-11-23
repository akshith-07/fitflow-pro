from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.organization import SubscriptionStatus


class OrganizationBase(BaseModel):
    name: str
    slug: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    timezone: str = "UTC"
    currency: str = "USD"


class OrganizationCreate(OrganizationBase):
    logo_url: Optional[str] = None
    primary_color: str = "#6366f1"
    address: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    logo_url: Optional[str]
    primary_color: str
    address: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]
    subscription_plan: str
    subscription_status: SubscriptionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
