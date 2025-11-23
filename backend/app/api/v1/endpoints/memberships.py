from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.membership import Membership, MembershipStatus
from app.models.member import Member
from app.schemas.membership import (
    MembershipCreate,
    MembershipUpdate,
    MembershipFreeze,
    MembershipCancel,
    MembershipResponse
)

router = APIRouter()


@router.get("", response_model=List[MembershipResponse])
def get_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[MembershipStatus] = None,
    member_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all memberships for the organization"""
    query = db.query(Membership).filter(
        Membership.organization_id == current_user.organization_id
    )

    if status_filter:
        query = query.filter(Membership.status == status_filter)

    if member_id:
        query = query.filter(Membership.member_id == member_id)

    memberships = query.offset(skip).limit(limit).all()
    return memberships


@router.post("", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
def create_membership(
    membership_data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new membership for a member"""
    # Check if user has permission
    if current_user.role not in ["gym_owner", "admin", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Verify member belongs to organization
    member = db.query(Member).filter(
        Member.id == membership_data.member_id,
        Member.organization_id == current_user.organization_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    new_membership = Membership(
        organization_id=current_user.organization_id,
        **membership_data.model_dump()
    )

    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    return new_membership


@router.get("/{membership_id}", response_model=MembershipResponse)
def get_membership(
    membership_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific membership"""
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.organization_id == current_user.organization_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )

    return membership


@router.put("/{membership_id}", response_model=MembershipResponse)
def update_membership(
    membership_id: UUID,
    membership_data: MembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a membership"""
    # Check if user has permission
    if current_user.role not in ["gym_owner", "admin", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.organization_id == current_user.organization_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )

    # Update fields
    update_data = membership_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(membership, field, value)

    db.commit()
    db.refresh(membership)

    return membership


@router.post("/{membership_id}/freeze", response_model=MembershipResponse)
def freeze_membership(
    membership_id: UUID,
    freeze_data: MembershipFreeze,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Freeze a membership"""
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.organization_id == current_user.organization_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )

    if membership.status != MembershipStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active memberships can be frozen"
        )

    membership.status = MembershipStatus.FROZEN
    membership.freeze_start_date = freeze_data.freeze_start_date
    membership.freeze_end_date = freeze_data.freeze_end_date

    # Extend membership end date
    freeze_days = (freeze_data.freeze_end_date - freeze_data.freeze_start_date).days
    from datetime import timedelta
    membership.end_date = membership.end_date + timedelta(days=freeze_days)

    db.commit()
    db.refresh(membership)

    return membership


@router.post("/{membership_id}/cancel", response_model=MembershipResponse)
def cancel_membership(
    membership_id: UUID,
    cancel_data: MembershipCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a membership"""
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.organization_id == current_user.organization_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )

    membership.status = MembershipStatus.CANCELLED
    membership.cancellation_date = date.today()
    membership.cancellation_reason = cancel_data.cancellation_reason
    membership.auto_renew = False

    db.commit()
    db.refresh(membership)

    return membership


@router.post("/{membership_id}/renew", response_model=MembershipResponse)
def renew_membership(
    membership_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Renew a membership"""
    membership = db.query(Membership).options(
        joinedload(Membership.plan)
    ).filter(
        Membership.id == membership_id,
        Membership.organization_id == current_user.organization_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )

    # Create new membership
    from datetime import timedelta
    new_membership = Membership(
        organization_id=membership.organization_id,
        member_id=membership.member_id,
        plan_id=membership.plan_id,
        start_date=membership.end_date + timedelta(days=1),
        end_date=membership.end_date + timedelta(days=membership.plan.duration_days + 1),
        auto_renew=membership.auto_renew,
        status=MembershipStatus.ACTIVE
    )

    # Mark old membership as expired
    membership.status = MembershipStatus.EXPIRED

    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    return new_membership
