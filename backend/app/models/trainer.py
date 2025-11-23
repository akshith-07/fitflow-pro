from sqlalchemy import Column, String, Numeric, Integer, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class Trainer(Base, BaseModel):
    __tablename__ = "trainers"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    specializations = Column(ARRAY(String), default=list)
    certifications = Column(JSON, default=list)
    bio = Column(String(1000), nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    commission_percentage = Column(Numeric(5, 2), default=0)
    rating = Column(Numeric(3, 2), default=0)
    total_sessions = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="trainer")
    classes = relationship("Class", back_populates="instructor")
    schedules = relationship("ClassSchedule", back_populates="instructor")
