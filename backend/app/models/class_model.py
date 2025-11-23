from sqlalchemy import Column, String, Integer, Boolean, JSON, Date, Time, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ClassStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingStatus(str, enum.Enum):
    BOOKED = "booked"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"


class Class(Base, BaseModel):
    __tablename__ = "classes"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    category = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("trainers.id"), nullable=True)
    room = Column(String(100), nullable=True)
    difficulty_level = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(JSON, nullable=True)
    image_url = Column(String(500), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="classes")
    instructor = relationship("Trainer", back_populates="classes")
    schedules = relationship("ClassSchedule", back_populates="class_obj", cascade="all, delete-orphan")


class ClassSchedule(Base, BaseModel):
    __tablename__ = "class_schedules"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False, index=True)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("trainers.id"), nullable=True)
    scheduled_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(SQLEnum(ClassStatus), default=ClassStatus.SCHEDULED)

    # Relationships
    class_obj = relationship("Class", back_populates="schedules")
    instructor = relationship("Trainer", back_populates="schedules")
    bookings = relationship("ClassBooking", back_populates="schedule", cascade="all, delete-orphan")


class ClassBooking(Base, BaseModel):
    __tablename__ = "class_bookings"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("class_schedules.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.BOOKED)
    booked_at = Column(DateTime, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    attended_at = Column(DateTime, nullable=True)

    # Relationships
    schedule = relationship("ClassSchedule", back_populates="bookings")
    member = relationship("Member", back_populates="bookings")
