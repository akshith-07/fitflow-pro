from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.equipment import Equipment, EquipmentStatus
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    MaintenanceLog
)

router = APIRouter()


@router.get("", response_model=List[EquipmentResponse])
def get_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[EquipmentStatus] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all equipment"""
    query = db.query(Equipment).filter(
        Equipment.organization_id == current_user.organization_id
    )

    if status_filter:
        query = query.filter(Equipment.status == status_filter)

    if category:
        query = query.filter(Equipment.category == category)

    equipment = query.offset(skip).limit(limit).all()
    return equipment


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new equipment"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    new_equipment = Equipment(
        organization_id=current_user.organization_id,
        **equipment_data.model_dump()
    )

    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)

    return new_equipment


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment_item(
    equipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific equipment"""
    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.organization_id == current_user.organization_id
    ).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    return equipment


@router.put("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(
    equipment_id: UUID,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update equipment"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.organization_id == current_user.organization_id
    ).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    update_data = equipment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)

    return equipment


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(
    equipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete equipment"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.organization_id == current_user.organization_id
    ).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    db.delete(equipment)
    db.commit()

    return None


@router.post("/{equipment_id}/maintenance", response_model=EquipmentResponse)
def log_maintenance(
    equipment_id: UUID,
    maintenance_data: MaintenanceLog,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Log maintenance for equipment"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.organization_id == current_user.organization_id
    ).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    # Update equipment maintenance dates
    equipment.last_maintenance_date = maintenance_data.maintenance_date
    if maintenance_data.next_maintenance_date:
        equipment.next_maintenance_date = maintenance_data.next_maintenance_date

    # TODO: Store maintenance log in a separate table for history

    db.commit()
    db.refresh(equipment)

    return equipment
