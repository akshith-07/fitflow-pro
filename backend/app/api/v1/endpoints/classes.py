from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.class_model import Class, ClassSchedule, ClassBooking, ClassStatus, BookingStatus
from app.models.member import Member
from app.schemas.class_schema import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassScheduleCreate,
    ClassScheduleUpdate,
    ClassScheduleResponse,
    ClassBookingCreate,
    ClassBookingResponse,
    ClassScheduleWithBookings
)

router = APIRouter()


# ===== CLASS CRUD =====
@router.get("", response_model=List[ClassResponse])
def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    instructor_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all classes"""
    query = db.query(Class).filter(
        Class.organization_id == current_user.organization_id
    )

    if category:
        query = query.filter(Class.category == category)

    if instructor_id:
        query = query.filter(Class.instructor_id == instructor_id)

    classes = query.offset(skip).limit(limit).all()
    return classes


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new class"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    new_class = Class(
        organization_id=current_user.organization_id,
        **class_data.model_dump()
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return new_class


@router.get("/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific class"""
    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.organization_id == current_user.organization_id
    ).first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    return class_obj


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: UUID,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a class"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.organization_id == current_user.organization_id
    ).first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    update_data = class_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(class_obj, field, value)

    db.commit()
    db.refresh(class_obj)

    return class_obj


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a class"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    class_obj = db.query(Class).filter(
        Class.id == class_id,
        Class.organization_id == current_user.organization_id
    ).first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    db.delete(class_obj)
    db.commit()

    return None


# ===== CLASS SCHEDULES =====
@router.get("/schedules/upcoming", response_model=List[ClassScheduleWithBookings])
def get_upcoming_schedules(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get upcoming class schedules"""
    from datetime import timedelta

    end_date = date.today() + timedelta(days=days)

    schedules = db.query(ClassSchedule).options(
        joinedload(ClassSchedule.bookings),
        joinedload(ClassSchedule.class_obj)
    ).filter(
        ClassSchedule.organization_id == current_user.organization_id,
        ClassSchedule.scheduled_date >= date.today(),
        ClassSchedule.scheduled_date <= end_date,
        ClassSchedule.status.in_([ClassStatus.SCHEDULED, ClassStatus.ONGOING])
    ).order_by(ClassSchedule.scheduled_date, ClassSchedule.start_time).all()

    result = []
    for schedule in schedules:
        # Calculate available spots
        total_bookings = len([b for b in schedule.bookings if b.status == BookingStatus.BOOKED])
        available_spots = schedule.class_obj.capacity - total_bookings

        schedule_dict = ClassScheduleWithBookings.from_orm(schedule)
        schedule_dict.available_spots = available_spots
        result.append(schedule_dict)

    return result


@router.post("/schedules", response_model=ClassScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule_data: ClassScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new class schedule"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Verify class exists
    class_obj = db.query(Class).filter(
        Class.id == schedule_data.class_id,
        Class.organization_id == current_user.organization_id
    ).first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    new_schedule = ClassSchedule(
        organization_id=current_user.organization_id,
        **schedule_data.model_dump()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return new_schedule


@router.put("/schedules/{schedule_id}", response_model=ClassScheduleResponse)
def update_schedule(
    schedule_id: UUID,
    schedule_data: ClassScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a class schedule"""
    if current_user.role not in ["gym_owner", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    schedule = db.query(ClassSchedule).filter(
        ClassSchedule.id == schedule_id,
        ClassSchedule.organization_id == current_user.organization_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    # TODO: Send notifications to booked members if time/date changed

    return schedule


# ===== CLASS BOOKINGS =====
@router.post("/schedules/{schedule_id}/book", response_model=ClassBookingResponse)
def book_class(
    schedule_id: UUID,
    member_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Book a class for a member"""
    # If member_id not provided, book for current user (if they are a member)
    if not member_id:
        if current_user.role != "member":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Member ID required for non-member users"
            )

        member = db.query(Member).filter(Member.user_id == current_user.id).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member profile not found"
            )
        member_id = member.id

    # Verify schedule exists
    schedule = db.query(ClassSchedule).options(
        joinedload(ClassSchedule.class_obj)
    ).filter(
        ClassSchedule.id == schedule_id,
        ClassSchedule.organization_id == current_user.organization_id
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    # Check if class is in the future
    if schedule.scheduled_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book past classes"
        )

    # Check if already booked
    existing_booking = db.query(ClassBooking).filter(
        ClassBooking.schedule_id == schedule_id,
        ClassBooking.member_id == member_id,
        ClassBooking.status.in_([BookingStatus.BOOKED, BookingStatus.WAITLISTED])
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already booked for this class"
        )

    # Check capacity
    current_bookings = db.query(func.count(ClassBooking.id)).filter(
        ClassBooking.schedule_id == schedule_id,
        ClassBooking.status == BookingStatus.BOOKED
    ).scalar() or 0

    # Determine booking status
    booking_status = BookingStatus.BOOKED
    if current_bookings >= schedule.class_obj.capacity:
        booking_status = BookingStatus.WAITLISTED

    new_booking = ClassBooking(
        organization_id=current_user.organization_id,
        schedule_id=schedule_id,
        member_id=member_id,
        status=booking_status,
        booked_at=datetime.now()
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a class booking"""
    booking = db.query(ClassBooking).filter(
        ClassBooking.id == booking_id,
        ClassBooking.organization_id == current_user.organization_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Check if user has permission to cancel
    if current_user.role == "member":
        member = db.query(Member).filter(Member.user_id == current_user.id).first()
        if not member or booking.member_id != member.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this booking"
            )

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.now()

    db.commit()

    # TODO: Promote from waitlist if applicable

    return None


@router.get("/my-bookings", response_model=List[ClassBookingResponse])
def get_my_bookings(
    upcoming_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get bookings for current member"""
    if current_user.role != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only members can access this endpoint"
        )

    member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member profile not found"
        )

    query = db.query(ClassBooking).join(ClassSchedule).filter(
        ClassBooking.member_id == member.id,
        ClassBooking.status.in_([BookingStatus.BOOKED, BookingStatus.WAITLISTED])
    )

    if upcoming_only:
        query = query.filter(ClassSchedule.scheduled_date >= date.today())

    bookings = query.order_by(ClassSchedule.scheduled_date, ClassSchedule.start_time).all()

    return bookings
