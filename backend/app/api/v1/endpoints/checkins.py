from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.checkin import CheckIn
from app.models.member import Member, MemberStatus
from app.models.membership import Membership, MembershipStatus
from app.schemas.checkin import (
    CheckInCreate,
    CheckInUpdate,
    CheckInResponse,
    QRCodeValidation,
    CheckInStats,
    MemberCheckInHistory
)

router = APIRouter()


@router.post("", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_check_in(
    checkin_data: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new check-in"""
    # Verify member exists and belongs to organization
    member = db.query(Member).filter(
        Member.id == checkin_data.member_id,
        Member.organization_id == current_user.organization_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Check if member is active
    if member.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Member is {member.status.value}. Cannot check in."
        )

    # Check if member has active membership
    active_membership = db.query(Membership).filter(
        Membership.member_id == member.id,
        Membership.status == MembershipStatus.ACTIVE,
        Membership.start_date <= date.today(),
        Membership.end_date >= date.today()
    ).first()

    if not active_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active membership found for this member"
        )

    # Check if already checked in today and not checked out
    existing_checkin = db.query(CheckIn).filter(
        CheckIn.member_id == member.id,
        CheckIn.check_out_time == None,
        func.date(CheckIn.check_in_time) == date.today()
    ).first()

    if existing_checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member is already checked in. Please check out first."
        )

    # Create check-in
    new_checkin = CheckIn(
        organization_id=current_user.organization_id,
        **checkin_data.model_dump()
    )

    db.add(new_checkin)
    db.commit()
    db.refresh(new_checkin)

    return new_checkin


@router.post("/qr-validate", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def check_in_with_qr(
    qr_data: QRCodeValidation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check in a member using QR code"""
    # Find member by QR code
    member = db.query(Member).filter(
        Member.qr_code == qr_data.qr_code,
        Member.organization_id == current_user.organization_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid QR code"
        )

    # Create check-in using the standard create endpoint logic
    from app.models.checkin import CheckInMethod
    checkin_data = CheckInCreate(
        member_id=member.id,
        check_in_time=datetime.now(),
        method=CheckInMethod.QR,
        location_id=qr_data.location_id
    )

    return create_check_in(checkin_data, db, current_user)


@router.get("", response_model=List[CheckInResponse])
def get_check_ins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    member_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get check-ins with filters"""
    query = db.query(CheckIn).filter(
        CheckIn.organization_id == current_user.organization_id
    )

    if member_id:
        query = query.filter(CheckIn.member_id == member_id)

    if start_date:
        query = query.filter(func.date(CheckIn.check_in_time) >= start_date)

    if end_date:
        query = query.filter(func.date(CheckIn.check_in_time) <= end_date)

    check_ins = query.order_by(CheckIn.check_in_time.desc()).offset(skip).limit(limit).all()
    return check_ins


@router.get("/current", response_model=List[CheckInResponse])
def get_current_check_ins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all members currently checked in (no checkout time)"""
    check_ins = db.query(CheckIn).filter(
        CheckIn.organization_id == current_user.organization_id,
        CheckIn.check_out_time == None,
        func.date(CheckIn.check_in_time) == date.today()
    ).all()

    return check_ins


@router.get("/stats", response_model=CheckInStats)
def get_check_in_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get check-in statistics"""
    today = date.today()

    # Total check-ins today
    total_today = db.query(func.count(CheckIn.id)).filter(
        CheckIn.organization_id == current_user.organization_id,
        func.date(CheckIn.check_in_time) == today
    ).scalar() or 0

    # Current occupancy
    current_occupancy = db.query(func.count(CheckIn.id)).filter(
        CheckIn.organization_id == current_user.organization_id,
        CheckIn.check_out_time == None,
        func.date(CheckIn.check_in_time) == today
    ).scalar() or 0

    # Peak hour (hour with most check-ins)
    peak_hour_query = db.query(
        func.extract('hour', CheckIn.check_in_time).label('hour'),
        func.count(CheckIn.id).label('count')
    ).filter(
        CheckIn.organization_id == current_user.organization_id,
        func.date(CheckIn.check_in_time) == today
    ).group_by('hour').order_by(func.count(CheckIn.id).desc()).first()

    peak_hour = f"{int(peak_hour_query[0])}:00" if peak_hour_query else None

    # Average duration
    avg_duration_query = db.query(
        func.avg(
            func.extract('epoch', CheckIn.check_out_time - CheckIn.check_in_time) / 60
        )
    ).filter(
        CheckIn.organization_id == current_user.organization_id,
        CheckIn.check_out_time != None,
        func.date(CheckIn.check_in_time) >= today - timedelta(days=7)
    ).scalar()

    avg_duration = float(avg_duration_query) if avg_duration_query else None

    return CheckInStats(
        total_check_ins_today=total_today,
        current_occupancy=current_occupancy,
        peak_hour_today=peak_hour,
        average_duration_minutes=avg_duration
    )


@router.get("/member/{member_id}", response_model=MemberCheckInHistory)
def get_member_check_in_history(
    member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get check-in history for a specific member"""
    # Verify member exists
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == current_user.organization_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Total visits
    total_visits = db.query(func.count(CheckIn.id)).filter(
        CheckIn.member_id == member_id
    ).scalar() or 0

    # Last visit
    last_visit = db.query(func.max(CheckIn.check_in_time)).filter(
        CheckIn.member_id == member_id
    ).scalar()

    # Average visits per week (last 12 weeks)
    twelve_weeks_ago = datetime.now() - timedelta(weeks=12)
    visits_last_12_weeks = db.query(func.count(CheckIn.id)).filter(
        CheckIn.member_id == member_id,
        CheckIn.check_in_time >= twelve_weeks_ago
    ).scalar() or 0
    avg_per_week = visits_last_12_weeks / 12

    # Get recent check-ins
    recent_checkins = db.query(CheckIn).filter(
        CheckIn.member_id == member_id
    ).order_by(CheckIn.check_in_time.desc()).limit(50).all()

    return MemberCheckInHistory(
        member_id=member_id,
        total_visits=total_visits,
        last_visit=last_visit,
        average_visits_per_week=avg_per_week,
        current_streak=0,  # TODO: Calculate streak
        longest_streak=0,  # TODO: Calculate streak
        check_ins=[CheckInResponse.from_orm(c) for c in recent_checkins]
    )


@router.put("/{checkin_id}", response_model=CheckInResponse)
def update_check_in(
    checkin_id: UUID,
    checkin_data: CheckInUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a check-in (mainly for checkout)"""
    checkin = db.query(CheckIn).filter(
        CheckIn.id == checkin_id,
        CheckIn.organization_id == current_user.organization_id
    ).first()

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )

    # Update fields
    update_data = checkin_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(checkin, field, value)

    db.commit()
    db.refresh(checkin)

    return checkin


@router.post("/{checkin_id}/checkout", response_model=CheckInResponse)
def checkout(
    checkin_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Checkout a member"""
    checkin = db.query(CheckIn).filter(
        CheckIn.id == checkin_id,
        CheckIn.organization_id == current_user.organization_id
    ).first()

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )

    if checkin.check_out_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member already checked out"
        )

    checkin.check_out_time = datetime.now()
    db.commit()
    db.refresh(checkin)

    return checkin
