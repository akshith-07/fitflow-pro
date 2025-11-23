from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    VISITED = "visited"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    WALK_IN = "walk_in"
    PHONE = "phone"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    EVENT = "event"
    OTHER = "other"


class Lead(Base, BaseModel):
    __tablename__ = "leads"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    source = Column(SQLEnum(LeadSource), nullable=False, default=LeadSource.OTHER)
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(String(1000), nullable=True)

    # Relationships
    organization = relationship("Organization")
    assigned_user = relationship("User")
