from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.lead import Lead, LeadStatus
from app.models.member import Member
from app.models.membership import Membership, MembershipStatus
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadConvert
)

router = APIRouter()


@router.get("", response_model=List[LeadResponse])
def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[LeadStatus] = None,
    assigned_to: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all leads"""
    if current_user.role not in ["gym_owner", "admin", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    query = db.query(Lead).filter(
        Lead.organization_id == current_user.organization_id
    )

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    if assigned_to:
        query = query.filter(Lead.assigned_to == assigned_to)

    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return leads


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new lead"""
    new_lead = Lead(
        organization_id=current_user.organization_id,
        **lead_data.model_dump()
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return new_lead


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific lead"""
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.organization_id == current_user.organization_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a lead"""
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.organization_id == current_user.organization_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    return lead


@router.post("/{lead_id}/convert", response_model=dict)
def convert_lead(
    lead_id: UUID,
    convert_data: LeadConvert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Convert a lead to a member"""
    if current_user.role not in ["gym_owner", "admin", "receptionist", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.organization_id == current_user.organization_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    if lead.status == LeadStatus.CONVERTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead already converted"
        )

    # Create user and member
    from app.core.security import get_password_hash
    from app.models.user import UserRole
    import uuid

    new_user = User(
        organization_id=current_user.organization_id,
        email=lead.email or f"{lead.phone}@temp.fitflowpro.com",
        password_hash=get_password_hash("changeMe123"),
        first_name=lead.name.split()[0] if lead.name else "New",
        last_name=lead.name.split()[1] if len(lead.name.split()) > 1 else "Member",
        phone=lead.phone,
        role=UserRole.MEMBER,
        is_active=True,
        is_verified=False
    )

    db.add(new_user)
    db.flush()

    new_member = Member(
        organization_id=current_user.organization_id,
        user_id=new_user.id,
        member_id=f"MEM-{str(uuid.uuid4())[:8].upper()}",
        qr_code=str(uuid.uuid4()),
        joined_at=date.today(),
        status="active"
    )

    db.add(new_member)
    db.flush()

    # Create membership
    from app.models.membership import MembershipPlan
    from datetime import timedelta

    plan = db.query(MembershipPlan).filter(
        MembershipPlan.id == convert_data.membership_plan_id,
        MembershipPlan.organization_id == current_user.organization_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership plan not found"
        )

    new_membership = Membership(
        organization_id=current_user.organization_id,
        member_id=new_member.id,
        plan_id=plan.id,
        start_date=convert_data.start_date,
        end_date=convert_data.start_date + timedelta(days=plan.duration_days),
        auto_renew=True,
        status=MembershipStatus.ACTIVE
    )

    db.add(new_membership)

    # Update lead status
    lead.status = LeadStatus.CONVERTED

    db.commit()

    return {
        "message": "Lead converted successfully",
        "member_id": str(new_member.id),
        "user_id": str(new_user.id)
    }


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a lead"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.organization_id == current_user.organization_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    db.delete(lead)
    db.commit()

    return None
