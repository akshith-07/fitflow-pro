from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    GYM_OWNER = "gym_owner"
    ADMIN = "admin"
    TRAINER = "trainer"
    RECEPTIONIST = "receptionist"
    MEMBER = "member"


class User(Base, BaseModel):
    __tablename__ = "users"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    profile_photo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    member = relationship("Member", back_populates="user", uselist=False)
    trainer = relationship("Trainer", back_populates="user", uselist=False)
    staff = relationship("Staff", back_populates="user", uselist=False)
