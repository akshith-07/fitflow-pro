from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_active_user
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.trainer import Trainer
from app.schemas.trainer import (
    TrainerCreate,
    TrainerUpdate,
    TrainerResponse,
    TrainerWithUser
)

router = APIRouter()


@router.get("", response_model=List[TrainerWithUser])
def get_trainers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all trainers"""
    trainers = db.query(Trainer).options(
        joinedload(Trainer.user)
    ).filter(
        Trainer.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()

    result = []
    for trainer in trainers:
        trainer_dict = TrainerWithUser.from_orm(trainer)
        trainer_dict.first_name = trainer.user.first_name
        trainer_dict.last_name = trainer.user.last_name
        trainer_dict.email = trainer.user.email
        trainer_dict.phone = trainer.user.phone
        trainer_dict.profile_photo_url = trainer.user.profile_photo_url
        result.append(trainer_dict)

    return result


@router.post("", response_model=TrainerResponse, status_code=status.HTTP_201_CREATED)
def create_trainer(
    trainer_data: TrainerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new trainer"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == trainer_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user first
    new_user = User(
        organization_id=current_user.organization_id,
        email=trainer_data.email,
        password_hash=get_password_hash("defaultPassword123"),  # TODO: Send password reset email
        first_name=trainer_data.first_name,
        last_name=trainer_data.last_name,
        phone=trainer_data.phone,
        role=UserRole.TRAINER,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.flush()

    # Create trainer profile
    trainer_dict = trainer_data.model_dump(exclude={"first_name", "last_name", "email", "phone"})
    new_trainer = Trainer(
        organization_id=current_user.organization_id,
        user_id=new_user.id,
        **trainer_dict
    )

    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)

    return new_trainer


@router.get("/{trainer_id}", response_model=TrainerWithUser)
def get_trainer(
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific trainer"""
    trainer = db.query(Trainer).options(
        joinedload(Trainer.user)
    ).filter(
        Trainer.id == trainer_id,
        Trainer.organization_id == current_user.organization_id
    ).first()

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )

    trainer_dict = TrainerWithUser.from_orm(trainer)
    trainer_dict.first_name = trainer.user.first_name
    trainer_dict.last_name = trainer.user.last_name
    trainer_dict.email = trainer.user.email
    trainer_dict.phone = trainer.user.phone
    trainer_dict.profile_photo_url = trainer.user.profile_photo_url

    return trainer_dict


@router.put("/{trainer_id}", response_model=TrainerResponse)
def update_trainer(
    trainer_id: UUID,
    trainer_data: TrainerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a trainer"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    trainer = db.query(Trainer).options(
        joinedload(Trainer.user)
    ).filter(
        Trainer.id == trainer_id,
        Trainer.organization_id == current_user.organization_id
    ).first()

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )

    # Update trainer fields
    update_data = trainer_data.model_dump(exclude_unset=True, exclude={"first_name", "last_name", "phone"})
    for field, value in update_data.items():
        setattr(trainer, field, value)

    # Update user fields if provided
    if trainer_data.first_name:
        trainer.user.first_name = trainer_data.first_name
    if trainer_data.last_name:
        trainer.user.last_name = trainer_data.last_name
    if trainer_data.phone:
        trainer.user.phone = trainer_data.phone

    db.commit()
    db.refresh(trainer)

    return trainer


@router.delete("/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trainer(
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a trainer"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    trainer = db.query(Trainer).filter(
        Trainer.id == trainer_id,
        Trainer.organization_id == current_user.organization_id
    ).first()

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )

    # Deactivate user instead of deleting
    trainer.user.is_active = False
    db.commit()

    return None
