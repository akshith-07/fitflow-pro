from sqlalchemy import Column, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, BaseModel
import enum


class EquipmentStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"


class Equipment(Base, BaseModel):
    __tablename__ = "equipment"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    purchase_date = Column(Date, nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    status = Column(SQLEnum(EquipmentStatus), default=EquipmentStatus.ACTIVE)
    last_maintenance_date = Column(Date, nullable=True)
    next_maintenance_date = Column(Date, nullable=True)

    # Relationships
    organization = relationship("Organization")
