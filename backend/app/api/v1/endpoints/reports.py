from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import io
import csv
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.member import Member
from app.models.membership import Membership
from app.models.payment import Payment
from app.models.checkin import CheckIn
from app.models.class_model import ClassSchedule, ClassBooking

router = APIRouter()


@router.post("/generate")
def generate_report(
    report_type: str = Query(..., description="Type of report: membership, financial, attendance, performance"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("json", description="Output format: json, csv, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a report based on type and date range"""
    org_id = current_user.organization_id

    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    if report_type == "membership":
        return generate_membership_report(org_id, start_date, end_date, format, db)
    elif report_type == "financial":
        return generate_financial_report(org_id, start_date, end_date, format, db)
    elif report_type == "attendance":
        return generate_attendance_report(org_id, start_date, end_date, format, db)
    elif report_type == "performance":
        return generate_performance_report(org_id, start_date, end_date, format, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report type: {report_type}"
        )


def generate_membership_report(org_id: UUID, start_date: datetime, end_date: datetime, format: str, db: Session):
    """Generate membership report"""
    # Active memberships
    active_memberships = db.query(Membership).filter(
        Membership.organization_id == org_id,
        Membership.status == "active"
    ).all()

    # New memberships in period
    new_memberships = db.query(Membership).filter(
        Membership.organization_id == org_id,
        Membership.created_at.between(start_date, end_date)
    ).all()

    # Expired memberships in period
    expired_memberships = db.query(Membership).filter(
        Membership.organization_id == org_id,
        Membership.status == "expired",
        Membership.end_date.between(start_date, end_date)
    ).all()

    # Cancelled memberships in period
    cancelled_memberships = db.query(Membership).filter(
        Membership.organization_id == org_id,
        Membership.status == "cancelled",
        Membership.cancellation_date.between(start_date.date(), end_date.date())
    ).all()

    report_data = {
        "report_type": "membership",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "summary": {
            "total_active": len(active_memberships),
            "new_memberships": len(new_memberships),
            "expired_memberships": len(expired_memberships),
            "cancelled_memberships": len(cancelled_memberships)
        },
        "details": {
            "active_memberships": [
                {
                    "member_id": str(m.member_id),
                    "plan_id": str(m.plan_id),
                    "start_date": m.start_date.isoformat(),
                    "end_date": m.end_date.isoformat(),
                    "auto_renew": m.auto_renew
                }
                for m in active_memberships
            ]
        }
    }

    if format == "csv":
        return export_to_csv(report_data, "membership_report")

    return report_data


def generate_financial_report(org_id: UUID, start_date: datetime, end_date: datetime, format: str, db: Session):
    """Generate financial report"""
    # Total revenue
    total_revenue = db.query(Payment).filter(
        Payment.organization_id == org_id,
        Payment.status == "completed",
        Payment.payment_date.between(start_date.date(), end_date.date())
    ).all()

    # Pending payments
    pending_payments = db.query(Payment).filter(
        Payment.organization_id == org_id,
        Payment.status == "pending"
    ).all()

    # Overdue payments
    overdue_payments = db.query(Payment).filter(
        Payment.organization_id == org_id,
        Payment.status == "pending",
        Payment.due_date < datetime.now().date()
    ).all()

    # Revenue by payment method
    from sqlalchemy import func
    revenue_by_method = db.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.organization_id == org_id,
        Payment.status == "completed",
        Payment.payment_date.between(start_date.date(), end_date.date())
    ).group_by(Payment.payment_method).all()

    report_data = {
        "report_type": "financial",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "summary": {
            "total_revenue": sum(p.amount for p in total_revenue),
            "total_payments": len(total_revenue),
            "pending_payments": len(pending_payments),
            "pending_amount": sum(p.amount for p in pending_payments),
            "overdue_payments": len(overdue_payments),
            "overdue_amount": sum(p.amount for p in overdue_payments)
        },
        "revenue_by_method": [
            {"method": method, "amount": float(amount)}
            for method, amount in revenue_by_method
        ],
        "details": {
            "payments": [
                {
                    "payment_id": str(p.id),
                    "member_id": str(p.member_id),
                    "amount": float(p.amount),
                    "payment_method": p.payment_method,
                    "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                    "status": p.status
                }
                for p in total_revenue
            ]
        }
    }

    if format == "csv":
        return export_to_csv(report_data, "financial_report")

    return report_data


def generate_attendance_report(org_id: UUID, start_date: datetime, end_date: datetime, format: str, db: Session):
    """Generate attendance report"""
    # Total check-ins
    checkins = db.query(CheckIn).filter(
        CheckIn.organization_id == org_id,
        CheckIn.check_in_time.between(start_date, end_date)
    ).all()

    # Unique members who checked in
    unique_members = db.query(CheckIn.member_id).filter(
        CheckIn.organization_id == org_id,
        CheckIn.check_in_time.between(start_date, end_date)
    ).distinct().count()

    # Daily breakdown
    from sqlalchemy import func
    daily_checkins = db.query(
        func.date(CheckIn.check_in_time).label('date'),
        func.count(CheckIn.id).label('count')
    ).filter(
        CheckIn.organization_id == org_id,
        CheckIn.check_in_time.between(start_date, end_date)
    ).group_by(func.date(CheckIn.check_in_time)).all()

    report_data = {
        "report_type": "attendance",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "summary": {
            "total_checkins": len(checkins),
            "unique_members": unique_members,
            "average_daily_checkins": len(checkins) / max((end_date - start_date).days, 1)
        },
        "daily_breakdown": [
            {"date": date.isoformat(), "count": count}
            for date, count in daily_checkins
        ],
        "details": {
            "checkins": [
                {
                    "checkin_id": str(c.id),
                    "member_id": str(c.member_id),
                    "check_in_time": c.check_in_time.isoformat(),
                    "check_out_time": c.check_out_time.isoformat() if c.check_out_time else None,
                    "method": c.method
                }
                for c in checkins
            ]
        }
    }

    if format == "csv":
        return export_to_csv(report_data, "attendance_report")

    return report_data


def generate_performance_report(org_id: UUID, start_date: datetime, end_date: datetime, format: str, db: Session):
    """Generate performance report"""
    from sqlalchemy import func

    # Class performance
    class_bookings = db.query(
        ClassSchedule.id,
        func.count(ClassBooking.id).label('total_bookings'),
        func.sum(func.case((ClassBooking.status == 'attended', 1), else_=0)).label('attended'),
        func.sum(func.case((ClassBooking.status == 'no_show', 1), else_=0)).label('no_shows')
    ).join(ClassBooking).filter(
        ClassSchedule.organization_id == org_id,
        ClassSchedule.scheduled_date.between(start_date.date(), end_date.date())
    ).group_by(ClassSchedule.id).all()

    # Membership retention
    total_members_start = db.query(Membership).filter(
        Membership.organization_id == org_id,
        Membership.created_at < start_date
    ).count()

    cancelled_in_period = db.query(Membership).filter(
        Membership.organization_id == org_id,
        Membership.status == "cancelled",
        Membership.cancellation_date.between(start_date.date(), end_date.date())
    ).count()

    retention_rate = ((total_members_start - cancelled_in_period) / total_members_start * 100) if total_members_start > 0 else 0

    report_data = {
        "report_type": "performance",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "summary": {
            "class_performance": {
                "total_classes": len(class_bookings),
                "total_bookings": sum(cb.total_bookings for cb in class_bookings),
                "total_attended": sum(cb.attended for cb in class_bookings),
                "total_no_shows": sum(cb.no_shows for cb in class_bookings),
                "attendance_rate": (sum(cb.attended for cb in class_bookings) / sum(cb.total_bookings for cb in class_bookings) * 100) if sum(cb.total_bookings for cb in class_bookings) > 0 else 0
            },
            "membership_retention": {
                "members_at_start": total_members_start,
                "cancelled_in_period": cancelled_in_period,
                "retention_rate": retention_rate
            }
        }
    }

    if format == "csv":
        return export_to_csv(report_data, "performance_report")

    return report_data


def export_to_csv(data: dict, filename: str):
    """Export report data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write summary section
    writer.writerow(["Report Type", data["report_type"]])
    writer.writerow(["Start Date", data["start_date"]])
    writer.writerow(["End Date", data["end_date"]])
    writer.writerow([])

    # Write summary data
    writer.writerow(["Summary"])
    for key, value in data["summary"].items():
        writer.writerow([key, value])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}_{datetime.now().strftime('%Y%m%d')}.csv"}
    )


@router.get("/scheduled")
def get_scheduled_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of scheduled reports"""
    # TODO: Implement scheduled reports storage and retrieval
    return {
        "message": "Scheduled reports feature coming soon",
        "scheduled_reports": []
    }


@router.get("/{report_id}")
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a previously generated report"""
    # TODO: Implement report storage and retrieval
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Report not found"
    )


@router.get("/{report_id}/download")
def download_report(
    report_id: UUID,
    format: str = Query("pdf", description="Download format: pdf, csv, excel"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a report in specified format"""
    # TODO: Implement report download in multiple formats
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Report not found"
    )
