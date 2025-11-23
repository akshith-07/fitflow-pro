from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel


class Staff(Base, BaseModel):
    __tablename__ = "staff"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    position = Column(String(100), nullable=True)
    salary = Column(Numeric(10, 2), nullable=True)
    hire_date = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="staff")
