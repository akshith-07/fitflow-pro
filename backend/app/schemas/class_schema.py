from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date, time, datetime
from uuid import UUID
from app.models.class_model import DifficultyLevel, ClassStatus, BookingStatus


# Class Schemas
class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    duration_minutes: int = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    instructor_id: Optional[UUID] = None
    room: Optional[str] = Field(None, max_length=100)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    is_recurring: bool = False
    recurrence_rule: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    capacity: Optional[int] = Field(None, gt=0)
    instructor_id: Optional[UUID] = None
    room: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None


class ClassResponse(ClassBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Class Schedule Schemas
class ClassScheduleBase(BaseModel):
    class_id: UUID
    instructor_id: Optional[UUID] = None
    scheduled_date: date
    start_time: time
    end_time: time


class ClassScheduleCreate(ClassScheduleBase):
    pass


class ClassScheduleUpdate(BaseModel):
    instructor_id: Optional[UUID] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[ClassStatus] = None


class ClassScheduleResponse(ClassScheduleBase):
    id: UUID
    organization_id: UUID
    status: ClassStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Class Booking Schemas
class ClassBookingCreate(BaseModel):
    schedule_id: UUID
    member_id: UUID


class ClassBookingUpdate(BaseModel):
    status: BookingStatus


class ClassBookingResponse(BaseModel):
    id: UUID
    organization_id: UUID
    schedule_id: UUID
    member_id: UUID
    status: BookingStatus
    booked_at: datetime
    cancelled_at: Optional[datetime] = None
    attended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Combined responses with nested data
class ClassScheduleWithBookings(ClassScheduleResponse):
    bookings: List[ClassBookingResponse] = []
    available_spots: int


class ClassWithSchedules(ClassResponse):
    schedules: List[ClassScheduleResponse] = []
