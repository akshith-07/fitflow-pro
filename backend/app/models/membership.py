from sqlalchemy import Column, String, Numeric, Integer, JSON, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class DurationType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    LIFETIME = "lifetime"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class MembershipPlan(Base, BaseModel):
    __tablename__ = "membership_plans"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    duration_type = Column(SQLEnum(DurationType), nullable=False)
    setup_fee = Column(Numeric(10, 2), default=0)
    features = Column(JSON, default=dict)
    access_hours = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="membership_plans")
    memberships = relationship("Membership", back_populates="plan")


class Membership(Base, BaseModel):
    __tablename__ = "memberships"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("membership_plans.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    auto_renew = Column(Boolean, default=True)
    status = Column(SQLEnum(MembershipStatus), default=MembershipStatus.ACTIVE)
    freeze_start_date = Column(Date, nullable=True)
    freeze_end_date = Column(Date, nullable=True)
    cancellation_date = Column(Date, nullable=True)
    cancellation_reason = Column(String(500), nullable=True)

    # Relationships
    member = relationship("Member", back_populates="memberships")
    plan = relationship("MembershipPlan", back_populates="memberships")
    payments = relationship("Payment", back_populates="membership")
