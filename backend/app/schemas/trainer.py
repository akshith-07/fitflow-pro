from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Trainer Schemas
class TrainerBase(BaseModel):
    specializations: List[str] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    bio: Optional[str] = Field(None, max_length=2000)
    hourly_rate: float = Field(default=0, ge=0)
    commission_percentage: float = Field(default=0, ge=0, le=100)


class TrainerCreate(TrainerBase):
    user_id: UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None


class TrainerUpdate(BaseModel):
    specializations: Optional[List[str]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    commission_percentage: Optional[float] = Field(None, ge=0, le=100)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class TrainerResponse(TrainerBase):
    id: UUID
    organization_id: UUID
    user_id: UUID
    rating: float
    total_sessions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainerWithUser(TrainerResponse):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None
