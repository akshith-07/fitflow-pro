from sqlalchemy import Column, String, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Organization(Base, BaseModel):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#6366f1")
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    address = Column(JSON, nullable=True)
    timezone = Column(String(50), default="UTC")
    currency = Column(String(3), default="USD")
    settings = Column(JSON, default=dict)
    subscription_plan = Column(String(50), default="basic")
    subscription_status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    members = relationship("Member", back_populates="organization", cascade="all, delete-orphan")
    membership_plans = relationship("MembershipPlan", back_populates="organization", cascade="all, delete-orphan")
    classes = relationship("Class", back_populates="organization", cascade="all, delete-orphan")
    check_ins = relationship("CheckIn", back_populates="organization", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="organization", cascade="all, delete-orphan")
