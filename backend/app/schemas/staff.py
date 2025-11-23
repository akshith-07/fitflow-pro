from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date, datetime
from uuid import UUID


# Staff Schemas
class StaffBase(BaseModel):
    position: str = Field(..., min_length=1, max_length=100)
    salary: Optional[float] = Field(None, ge=0)
    hire_date: date


class StaffCreate(StaffBase):
    user_id: UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None


class StaffUpdate(BaseModel):
    position: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0)
    hire_date: Optional[date] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class StaffResponse(StaffBase):
    id: UUID
    organization_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StaffWithUser(StaffResponse):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None
    role: str
    is_active: bool
