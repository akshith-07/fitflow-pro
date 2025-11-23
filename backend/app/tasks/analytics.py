from celery import shared_task
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.checkin import CheckIn
from app.models.payment import Payment, PaymentStatus
from app.models.membership import Membership, MembershipStatus
from app.models.member import Member
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.analytics.update_weekly_analytics")
def update_weekly_analytics():
    """Calculate and store weekly analytics"""
    db: Session = SessionLocal()

    try:
        # Calculate date range for last week
        today = date.today()
        week_ago = today - timedelta(days=7)

        # Calculate various metrics
        metrics = {}

        # Total check-ins last week
        total_checkins = db.query(func.count(CheckIn.id)).filter(
            func.date(CheckIn.check_in_time) >= week_ago,
            func.date(CheckIn.check_in_time) < today
        ).scalar() or 0

        metrics['total_checkins'] = total_checkins

        # Total revenue last week
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= week_ago,
            Payment.payment_date < today
        ).scalar() or 0

        metrics['total_revenue'] = float(total_revenue)

        # New members last week
        new_members = db.query(func.count(Member.id)).filter(
            Member.joined_at >= week_ago,
            Member.joined_at < today
        ).scalar() or 0

        metrics['new_members'] = new_members

        # Active memberships
        active_memberships = db.query(func.count(Membership.id)).filter(
            Membership.status == MembershipStatus.ACTIVE
        ).scalar() or 0

        metrics['active_memberships'] = active_memberships

        # TODO: Store these metrics in a separate analytics table
        # For now, just log them

        logger.info(f"Weekly analytics calculated: {metrics}")

    except Exception as e:
        logger.error(f"Error in update_weekly_analytics task: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.analytics.calculate_churn_rate")
def calculate_churn_rate():
    """Calculate monthly churn rate"""
    db: Session = SessionLocal()

    try:
        # Get the first and last day of last month
        today = date.today()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)

        # Members at start of month
        members_start = db.query(func.count(Member.id)).filter(
            Member.joined_at < first_day_last_month
        ).scalar() or 0

        # Cancelled memberships during the month
        cancelled = db.query(func.count(Membership.id)).filter(
            Membership.status == MembershipStatus.CANCELLED,
            Membership.cancellation_date >= first_day_last_month,
            Membership.cancellation_date <= last_day_last_month
        ).scalar() or 0

        # Calculate churn rate
        if members_start > 0:
            churn_rate = (cancelled / members_start) * 100
        else:
            churn_rate = 0

        logger.info(f"Monthly churn rate: {churn_rate:.2f}%")

        # TODO: Store churn rate in analytics table

    except Exception as e:
        logger.error(f"Error in calculate_churn_rate task: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.analytics.predict_churn_risk")
def predict_churn_risk():
    """Predict which members are at risk of churning"""
    db: Session = SessionLocal()

    try:
        # Simple churn risk prediction based on:
        # 1. Low attendance (< 2 visits per week)
        # 2. No visit in last 14 days
        # 3. Membership expiring soon

        two_weeks_ago = date.today() - timedelta(days=14)
        eight_weeks_ago = date.today() - timedelta(days=56)

        # Get all active members
        active_members = db.query(Member).join(Membership).filter(
            Membership.status == MembershipStatus.ACTIVE
        ).all()

        at_risk_members = []

        for member in active_members:
            risk_score = 0

            # Check attendance in last 8 weeks
            checkins_count = db.query(func.count(CheckIn.id)).filter(
                CheckIn.member_id == member.id,
                func.date(CheckIn.check_in_time) >= eight_weeks_ago
            ).scalar() or 0

            avg_per_week = checkins_count / 8

            if avg_per_week < 2:
                risk_score += 30

            # Check last visit
            last_checkin = db.query(CheckIn).filter(
                CheckIn.member_id == member.id
            ).order_by(CheckIn.check_in_time.desc()).first()

            if not last_checkin or last_checkin.check_in_time.date() < two_weeks_ago:
                risk_score += 40

            # Check membership expiry
            active_membership = db.query(Membership).filter(
                Membership.member_id == member.id,
                Membership.status == MembershipStatus.ACTIVE
            ).first()

            if active_membership:
                days_until_expiry = (active_membership.end_date - date.today()).days
                if days_until_expiry <= 30 and not active_membership.auto_renew:
                    risk_score += 30

            if risk_score >= 50:
                at_risk_members.append({
                    'member_id': str(member.id),
                    'risk_score': risk_score,
                    'email': member.user.email
                })

        logger.info(f"Found {len(at_risk_members)} members at risk of churning")

        # TODO: Store at-risk members in database for targeted campaigns
        # TODO: Send notifications to gym staff about at-risk members

    except Exception as e:
        logger.error(f"Error in predict_churn_risk task: {str(e)}")
    finally:
        db.close()
