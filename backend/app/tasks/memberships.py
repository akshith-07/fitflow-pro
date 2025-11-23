from celery import shared_task
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.membership import Membership, MembershipStatus
from app.models.checkin import CheckIn
from app.services.notification import NotificationManager
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.memberships.check_expiring_memberships")
def check_expiring_memberships():
    """Check for memberships expiring soon and send notifications"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        # Get memberships expiring in 7 days
        seven_days_later = date.today() + timedelta(days=7)

        expiring_memberships = db.query(Membership).filter(
            Membership.status == MembershipStatus.ACTIVE,
            Membership.end_date == seven_days_later
        ).all()

        logger.info(f"Found {len(expiring_memberships)} memberships expiring in 7 days")

        for membership in expiring_memberships:
            try:
                member = membership.member
                plan = membership.plan

                # Send expiry notification
                notification_manager.send_email(
                    recipient=member.user.email,
                    subject="Your Membership Expires Soon",
                    content=f"""
                    Hi {member.user.first_name},

                    This is a reminder that your {plan.name} membership expires on {membership.end_date}.

                    {'Your membership will automatically renew.' if membership.auto_renew else 'Please renew your membership to continue enjoying our facilities.'}

                    If you have any questions, please contact us.

                    Thank you for being a valued member!
                    The FitFlow Pro Team
                    """
                )

                # Send SMS if phone available
                if member.user.phone:
                    notification_manager.send_sms(
                        recipient=member.user.phone,
                        content=f"Your {plan.name} membership expires on {membership.end_date}. {'Auto-renewal is ON.' if membership.auto_renew else 'Please renew to continue.'}"
                    )

                logger.info(f"Expiry notification sent for membership {membership.id}")

            except Exception as e:
                logger.error(f"Error sending expiry notification for membership {membership.id}: {str(e)}")
                continue

        # Also check and expire memberships that ended yesterday
        yesterday = date.today() - timedelta(days=1)

        expired_memberships = db.query(Membership).filter(
            Membership.status == MembershipStatus.ACTIVE,
            Membership.end_date == yesterday,
            Membership.auto_renew == False
        ).all()

        for membership in expired_memberships:
            membership.status = MembershipStatus.EXPIRED
            logger.info(f"Membership {membership.id} marked as expired")

        db.commit()

        logger.info("Expiring memberships check completed")

    except Exception as e:
        logger.error(f"Error in check_expiring_memberships task: {str(e)}")
        db.rollback()
    finally:
        db.close()


@shared_task(name="app.tasks.memberships.check_inactive_members")
def check_inactive_members():
    """Check for inactive members and send re-engagement emails"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        # Define inactive as no check-in in the last 14 days
        cutoff_date = date.today() - timedelta(days=14)

        # Get active memberships
        active_memberships = db.query(Membership).filter(
            Membership.status == MembershipStatus.ACTIVE
        ).all()

        inactive_count = 0

        for membership in active_memberships:
            try:
                # Check last check-in
                last_checkin = db.query(CheckIn).filter(
                    CheckIn.member_id == membership.member_id
                ).order_by(CheckIn.check_in_time.desc()).first()

                if not last_checkin or last_checkin.check_in_time.date() < cutoff_date:
                    # Member is inactive
                    member = membership.member

                    # Send re-engagement email
                    notification_manager.send_email(
                        recipient=member.user.email,
                        subject="We Miss You at FitFlow Pro!",
                        content=f"""
                        Hi {member.user.first_name},

                        We noticed you haven't been to the gym in a while. We hope everything is okay!

                        Your membership is still active, and we'd love to see you back. Here are some things happening:

                        - New classes added this month
                        - Personal training sessions available
                        - Updated equipment

                        Need help getting back on track? Our trainers are here to help you reach your fitness goals.

                        See you soon!
                        The FitFlow Pro Team
                        """
                    )

                    inactive_count += 1
                    logger.info(f"Re-engagement email sent to member {member.id}")

            except Exception as e:
                logger.error(f"Error processing member {membership.member_id}: {str(e)}")
                continue

        logger.info(f"Inactive members check completed. {inactive_count} re-engagement emails sent")

    except Exception as e:
        logger.error(f"Error in check_inactive_members task: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.memberships.unfreeze_memberships")
def unfreeze_memberships():
    """Automatically unfreeze memberships that have reached their unfreeze date"""
    db: Session = SessionLocal()

    try:
        today = date.today()

        # Get frozen memberships with freeze end date today or earlier
        frozen_memberships = db.query(Membership).filter(
            Membership.status == MembershipStatus.FROZEN,
            Membership.freeze_end_date <= today
        ).all()

        logger.info(f"Found {len(frozen_memberships)} memberships to unfreeze")

        for membership in frozen_memberships:
            try:
                membership.status = MembershipStatus.ACTIVE
                membership.freeze_start_date = None
                membership.freeze_end_date = None

                logger.info(f"Membership {membership.id} unfrozen")

            except Exception as e:
                logger.error(f"Error unfreezing membership {membership.id}: {str(e)}")
                continue

        db.commit()

        logger.info("Unfreeze memberships task completed")

    except Exception as e:
        logger.error(f"Error in unfreeze_memberships task: {str(e)}")
        db.rollback()
    finally:
        db.close()
