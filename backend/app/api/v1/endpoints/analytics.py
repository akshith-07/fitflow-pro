from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import Optional
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.member import Member
from app.models.membership import Membership
from app.models.checkin import CheckIn
from app.models.payment import Payment
from app.models.class_model import Class, ClassSchedule, ClassBooking
from app.schemas.analytics import (
    DashboardMetrics,
    RevenueAnalytics,
    MemberAnalytics,
    AttendanceAnalytics,
    ClassAnalytics
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard metrics"""
    org_id = current_user.organization_id
    today = datetime.now().date()

    # Current occupancy - members checked in today who haven't checked out
    current_occupancy = db.query(CheckIn).filter(
        and_(
            CheckIn.organization_id == org_id,
            func.date(CheckIn.check_in_time) == today,
            CheckIn.check_out_time.is_(None)
        )
    ).count()

    # Total check-ins today
    checkins_today = db.query(CheckIn).filter(
        and_(
            CheckIn.organization_id == org_id,
            func.date(CheckIn.check_in_time) == today
        )
    ).count()

    # Yesterday's check-ins for comparison
    yesterday = today - timedelta(days=1)
    checkins_yesterday = db.query(CheckIn).filter(
        and_(
            CheckIn.organization_id == org_id,
            func.date(CheckIn.check_in_time) == yesterday
        )
    ).count()

    # Revenue today
    revenue_today = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.organization_id == org_id,
            Payment.status == "completed",
            func.date(Payment.payment_date) == today
        )
    ).scalar() or 0

    # Revenue yesterday
    revenue_yesterday = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.organization_id == org_id,
            Payment.status == "completed",
            func.date(Payment.payment_date) == yesterday
        )
    ).scalar() or 0

    # Active memberships
    active_memberships = db.query(Membership).filter(
        and_(
            Membership.organization_id == org_id,
            Membership.status == "active"
        )
    ).count()

    # New members today
    new_members_today = db.query(Member).filter(
        and_(
            Member.organization_id == org_id,
            func.date(Member.created_at) == today
        )
    ).count()

    # Expiring memberships this week
    week_from_now = today + timedelta(days=7)
    expiring_memberships = db.query(Membership).filter(
        and_(
            Membership.organization_id == org_id,
            Membership.status == "active",
            Membership.end_date.between(today, week_from_now)
        )
    ).count()

    # Overdue payments
    overdue_payments = db.query(Payment).filter(
        and_(
            Payment.organization_id == org_id,
            Payment.status == "pending",
            Payment.due_date < today
        )
    ).count()

    # Class bookings today
    class_bookings_today = db.query(ClassBooking).join(ClassSchedule).filter(
        and_(
            ClassSchedule.organization_id == org_id,
            ClassSchedule.scheduled_date == today
        )
    ).count()

    return {
        "current_occupancy": current_occupancy,
        "checkins_today": checkins_today,
        "checkins_yesterday": checkins_yesterday,
        "revenue_today": float(revenue_today),
        "revenue_yesterday": float(revenue_yesterday),
        "active_memberships": active_memberships,
        "new_members_today": new_members_today,
        "expiring_memberships_this_week": expiring_memberships,
        "overdue_payments": overdue_payments,
        "class_bookings_today": class_bookings_today
    }


@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get revenue analytics"""
    org_id = current_user.organization_id

    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    # Total revenue in period
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.organization_id == org_id,
            Payment.status == "completed",
            Payment.payment_date.between(start_date, end_date)
        )
    ).scalar() or 0

    # Monthly recurring revenue (active memberships)
    mrr_query = db.query(
        func.sum(Payment.amount)
    ).join(Membership).filter(
        and_(
            Payment.organization_id == org_id,
            Membership.status == "active",
            Membership.auto_renew == True
        )
    ).scalar() or 0

    # Revenue by payment method
    revenue_by_method = db.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('total')
    ).filter(
        and_(
            Payment.organization_id == org_id,
            Payment.status == "completed",
            Payment.payment_date.between(start_date, end_date)
        )
    ).group_by(Payment.payment_method).all()

    # Daily revenue trend
    daily_revenue = db.query(
        func.date(Payment.payment_date).label('date'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        and_(
            Payment.organization_id == org_id,
            Payment.status == "completed",
            Payment.payment_date.between(start_date, end_date)
        )
    ).group_by(func.date(Payment.payment_date)).all()

    return {
        "total_revenue": float(total_revenue),
        "mrr": float(mrr_query),
        "arr": float(mrr_query * 12),
        "revenue_by_payment_method": [
            {"method": method, "amount": float(amount)}
            for method, amount in revenue_by_method
        ],
        "daily_revenue": [
            {"date": date, "revenue": float(revenue)}
            for date, revenue in daily_revenue
        ],
        "start_date": start_date,
        "end_date": end_date
    }


@router.get("/members", response_model=MemberAnalytics)
def get_member_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get member analytics"""
    org_id = current_user.organization_id

    # Total members by status
    total_active = db.query(Membership).filter(
        and_(
            Membership.organization_id == org_id,
            Membership.status == "active"
        )
    ).count()

    total_frozen = db.query(Membership).filter(
        and_(
            Membership.organization_id == org_id,
            Membership.status == "frozen"
        )
    ).count()

    total_expired = db.query(Membership).filter(
        and_(
            Membership.organization_id == org_id,
            Membership.status == "expired"
        )
    ).count()

    total_cancelled = db.query(Membership).filter(
        and_(
            Membership.organization_id == org_id,
            Membership.status == "cancelled"
        )
    ).count()

    # Member growth trend (last 12 months)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    member_growth = db.query(
        extract('year', Member.created_at).label('year'),
        extract('month', Member.created_at).label('month'),
        func.count(Member.id).label('count')
    ).filter(
        and_(
            Member.organization_id == org_id,
            Member.created_at >= twelve_months_ago
        )
    ).group_by('year', 'month').all()

    # Demographics - gender distribution
    gender_distribution = db.query(
        Member.gender,
        func.count(Member.id).label('count')
    ).filter(
        Member.organization_id == org_id
    ).group_by(Member.gender).all()

    return {
        "total_active": total_active,
        "total_frozen": total_frozen,
        "total_expired": total_expired,
        "total_cancelled": total_cancelled,
        "total_members": total_active + total_frozen + total_expired + total_cancelled,
        "member_growth": [
            {"year": int(year), "month": int(month), "count": count}
            for year, month, count in member_growth
        ],
        "gender_distribution": [
            {"gender": gender or "not_specified", "count": count}
            for gender, count in gender_distribution
        ]
    }


@router.get("/attendance", response_model=AttendanceAnalytics)
def get_attendance_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance analytics"""
    org_id = current_user.organization_id

    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    # Total check-ins in period
    total_checkins = db.query(CheckIn).filter(
        and_(
            CheckIn.organization_id == org_id,
            CheckIn.check_in_time.between(start_date, end_date)
        )
    ).count()

    # Daily check-ins trend
    daily_checkins = db.query(
        func.date(CheckIn.check_in_time).label('date'),
        func.count(CheckIn.id).label('count')
    ).filter(
        and_(
            CheckIn.organization_id == org_id,
            CheckIn.check_in_time.between(start_date, end_date)
        )
    ).group_by(func.date(CheckIn.check_in_time)).all()

    # Peak hours (hour of day distribution)
    peak_hours = db.query(
        extract('hour', CheckIn.check_in_time).label('hour'),
        func.count(CheckIn.id).label('count')
    ).filter(
        and_(
            CheckIn.organization_id == org_id,
            CheckIn.check_in_time.between(start_date, end_date)
        )
    ).group_by('hour').all()

    # Average session duration (for check-ins with check-out)
    avg_duration = db.query(
        func.avg(
            extract('epoch', CheckIn.check_out_time - CheckIn.check_in_time)
        )
    ).filter(
        and_(
            CheckIn.organization_id == org_id,
            CheckIn.check_out_time.isnot(None),
            CheckIn.check_in_time.between(start_date, end_date)
        )
    ).scalar() or 0

    return {
        "total_checkins": total_checkins,
        "daily_checkins": [
            {"date": date, "count": count}
            for date, count in daily_checkins
        ],
        "peak_hours": [
            {"hour": int(hour), "count": count}
            for hour, count in peak_hours
        ],
        "average_session_duration_minutes": float(avg_duration / 60) if avg_duration else 0,
        "start_date": start_date,
        "end_date": end_date
    }


@router.get("/classes", response_model=ClassAnalytics)
def get_class_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get class analytics"""
    org_id = current_user.organization_id

    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    # Most popular classes (by bookings)
    popular_classes = db.query(
        Class.name,
        func.count(ClassBooking.id).label('bookings')
    ).join(ClassSchedule).join(ClassBooking).filter(
        and_(
            Class.organization_id == org_id,
            ClassSchedule.scheduled_date.between(start_date.date(), end_date.date())
        )
    ).group_by(Class.id, Class.name).order_by(func.count(ClassBooking.id).desc()).limit(10).all()

    # Average attendance per class
    avg_attendance = db.query(
        Class.name,
        func.avg(
            func.count(ClassBooking.id)
        ).label('avg_attendance')
    ).join(ClassSchedule).join(ClassBooking).filter(
        and_(
            Class.organization_id == org_id,
            ClassSchedule.scheduled_date.between(start_date.date(), end_date.date()),
            ClassBooking.status == "attended"
        )
    ).group_by(Class.id, Class.name).all()

    # No-show rate
    total_bookings = db.query(ClassBooking).join(ClassSchedule).filter(
        and_(
            ClassSchedule.organization_id == org_id,
            ClassSchedule.scheduled_date.between(start_date.date(), end_date.date())
        )
    ).count()

    no_shows = db.query(ClassBooking).join(ClassSchedule).filter(
        and_(
            ClassSchedule.organization_id == org_id,
            ClassSchedule.scheduled_date.between(start_date.date(), end_date.date()),
            ClassBooking.status == "no_show"
        )
    ).count()

    no_show_rate = (no_shows / total_bookings * 100) if total_bookings > 0 else 0

    return {
        "popular_classes": [
            {"class_name": name, "bookings": bookings}
            for name, bookings in popular_classes
        ],
        "average_attendance": [
            {"class_name": name, "avg_attendance": float(avg)}
            for name, avg in avg_attendance
        ],
        "total_bookings": total_bookings,
        "no_shows": no_shows,
        "no_show_rate": float(no_show_rate),
        "start_date": start_date,
        "end_date": end_date
    }
