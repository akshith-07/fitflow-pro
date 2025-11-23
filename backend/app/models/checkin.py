from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class CheckInMethod(str, enum.Enum):
    QR = "qr"
    NFC = "nfc"
    MANUAL = "manual"
    BIOMETRIC = "biometric"
    APP = "app"


class CheckIn(Base, BaseModel):
    __tablename__ = "check_ins"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True)
    check_in_time = Column(DateTime, nullable=False, index=True)
    check_out_time = Column(DateTime, nullable=True)
    method = Column(SQLEnum(CheckInMethod), nullable=False)
    location_id = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="check_ins")
    member = relationship("Member", back_populates="check_ins")
