from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.deps import get_db, get_current_user, get_current_active_user
from app.models.user import User
from app.models.membership import MembershipPlan
from app.schemas.membership import (
    MembershipPlanCreate,
    MembershipPlanUpdate,
    MembershipPlanResponse
)

router = APIRouter()


@router.get("", response_model=List[MembershipPlanResponse])
def get_membership_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all membership plans for the organization"""
    query = db.query(MembershipPlan).filter(
        MembershipPlan.organization_id == current_user.organization_id
    )

    if is_active is not None:
        query = query.filter(MembershipPlan.is_active == is_active)

    plans = query.offset(skip).limit(limit).all()
    return plans


@router.post("", response_model=MembershipPlanResponse, status_code=status.HTTP_201_CREATED)
def create_membership_plan(
    plan_data: MembershipPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new membership plan"""
    # Check if user has permission (admin, owner)
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    new_plan = MembershipPlan(
        organization_id=current_user.organization_id,
        **plan_data.model_dump()
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return new_plan


@router.get("/{plan_id}", response_model=MembershipPlanResponse)
def get_membership_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific membership plan"""
    plan = db.query(MembershipPlan).filter(
        MembershipPlan.id == plan_id,
        MembershipPlan.organization_id == current_user.organization_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership plan not found"
        )

    return plan


@router.put("/{plan_id}", response_model=MembershipPlanResponse)
def update_membership_plan(
    plan_id: UUID,
    plan_data: MembershipPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a membership plan"""
    # Check if user has permission
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    plan = db.query(MembershipPlan).filter(
        MembershipPlan.id == plan_id,
        MembershipPlan.organization_id == current_user.organization_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership plan not found"
        )

    # Update fields
    update_data = plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a membership plan (soft delete by marking inactive)"""
    # Check if user has permission
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    plan = db.query(MembershipPlan).filter(
        MembershipPlan.id == plan_id,
        MembershipPlan.organization_id == current_user.organization_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership plan not found"
        )

    # Soft delete by marking inactive
    plan.is_active = False
    db.commit()

    return None
