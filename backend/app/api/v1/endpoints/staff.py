from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_active_user
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.staff import Staff
from app.schemas.staff import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
    StaffWithUser
)

router = APIRouter()


@router.get("", response_model=List[StaffWithUser])
def get_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all staff members"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    staff = db.query(Staff).options(
        joinedload(Staff.user)
    ).filter(
        Staff.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()

    result = []
    for s in staff:
        staff_dict = StaffWithUser.from_orm(s)
        staff_dict.first_name = s.user.first_name
        staff_dict.last_name = s.user.last_name
        staff_dict.email = s.user.email
        staff_dict.phone = s.user.phone
        staff_dict.profile_photo_url = s.user.profile_photo_url
        staff_dict.role = s.user.role.value
        staff_dict.is_active = s.user.is_active
        result.append(staff_dict)

    return result


@router.post("", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new staff member"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == staff_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user first
    new_user = User(
        organization_id=current_user.organization_id,
        email=staff_data.email,
        password_hash=get_password_hash("defaultPassword123"),
        first_name=staff_data.first_name,
        last_name=staff_data.last_name,
        phone=staff_data.phone,
        role=UserRole.RECEPTIONIST,  # Default role
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.flush()

    # Create staff profile
    staff_dict = staff_data.model_dump(exclude={"first_name", "last_name", "email", "phone"})
    new_staff = Staff(
        organization_id=current_user.organization_id,
        user_id=new_user.id,
        **staff_dict
    )

    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return new_staff


@router.get("/{staff_id}", response_model=StaffWithUser)
def get_staff_member(
    staff_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific staff member"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    staff = db.query(Staff).options(
        joinedload(Staff.user)
    ).filter(
        Staff.id == staff_id,
        Staff.organization_id == current_user.organization_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    staff_dict = StaffWithUser.from_orm(staff)
    staff_dict.first_name = staff.user.first_name
    staff_dict.last_name = staff.user.last_name
    staff_dict.email = staff.user.email
    staff_dict.phone = staff.user.phone
    staff_dict.profile_photo_url = staff.user.profile_photo_url
    staff_dict.role = staff.user.role.value
    staff_dict.is_active = staff.user.is_active

    return staff_dict


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: UUID,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a staff member"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    staff = db.query(Staff).options(
        joinedload(Staff.user)
    ).filter(
        Staff.id == staff_id,
        Staff.organization_id == current_user.organization_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    # Update staff fields
    update_data = staff_data.model_dump(exclude_unset=True, exclude={"first_name", "last_name", "phone"})
    for field, value in update_data.items():
        setattr(staff, field, value)

    # Update user fields
    if staff_data.first_name:
        staff.user.first_name = staff_data.first_name
    if staff_data.last_name:
        staff.user.last_name = staff_data.last_name
    if staff_data.phone:
        staff.user.phone = staff_data.phone

    db.commit()
    db.refresh(staff)

    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a staff member"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    staff = db.query(Staff).filter(
        Staff.id == staff_id,
        Staff.organization_id == current_user.organization_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )

    # Deactivate user instead of deleting
    staff.user.is_active = False
    db.commit()

    return None
