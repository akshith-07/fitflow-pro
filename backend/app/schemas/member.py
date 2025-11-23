from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from app.models.member import Gender, MemberStatus


class MemberBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None
    fitness_goals: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class MemberCreate(MemberBase):
    user_id: UUID
    member_id: str
    joined_at: date


class MemberUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[Dict[str, Any]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None
    fitness_goals: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[MemberStatus] = None


class MemberResponse(MemberBase):
    id: UUID
    organization_id: UUID
    user_id: UUID
    member_id: str
    address: Optional[Dict[str, Any]]
    profile_photo_url: Optional[str]
    qr_code: Optional[str]
    status: MemberStatus
    joined_at: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
