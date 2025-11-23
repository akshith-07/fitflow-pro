from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.checkin import CheckInMethod


# CheckIn Schemas
class CheckInBase(BaseModel):
    member_id: UUID
    check_in_time: datetime
    method: CheckInMethod = CheckInMethod.QR


class CheckInCreate(CheckInBase):
    location_id: Optional[UUID] = None


class CheckInUpdate(BaseModel):
    check_out_time: Optional[datetime] = None


class CheckInResponse(CheckInBase):
    id: UUID
    organization_id: UUID
    check_out_time: Optional[datetime] = None
    location_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# QR Code Validation
class QRCodeValidation(BaseModel):
    qr_code: str
    location_id: Optional[UUID] = None


class CheckInStats(BaseModel):
    total_check_ins_today: int
    current_occupancy: int
    peak_hour_today: Optional[str] = None
    average_duration_minutes: Optional[float] = None


# Member Check-In History
class MemberCheckInHistory(BaseModel):
    member_id: UUID
    total_visits: int
    last_visit: Optional[datetime] = None
    average_visits_per_week: float
    current_streak: int
    longest_streak: int
    check_ins: list = []
