from sqlalchemy import Column, String, Date, JSON, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MemberStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Member(Base, BaseModel):
    __tablename__ = "members"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    member_id = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)
    address = Column(JSON, nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    medical_notes = Column(String(1000), nullable=True)
    fitness_goals = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), default=list)
    profile_photo_url = Column(String(500), nullable=True)
    qr_code = Column(String(255), nullable=True, unique=True)
    status = Column(SQLEnum(MemberStatus), default=MemberStatus.ACTIVE)
    joined_at = Column(Date, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="member")
    memberships = relationship("Membership", back_populates="member", cascade="all, delete-orphan")
    check_ins = relationship("CheckIn", back_populates="member", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="member", cascade="all, delete-orphan")
    bookings = relationship("ClassBooking", back_populates="member", cascade="all, delete-orphan")
