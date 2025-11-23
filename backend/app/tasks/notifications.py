from celery import shared_task
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.payment import Payment, PaymentStatus
from app.models.class_model import ClassSchedule, ClassBooking, ClassStatus, BookingStatus
from app.services.notification import NotificationManager
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.notifications.send_payment_reminders")
def send_payment_reminders():
    """Send payment reminders for upcoming due dates"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        # Get payments due in 3 days
        reminder_date = date.today() + timedelta(days=3)

        pending_payments = db.query(Payment).filter(
            Payment.status == PaymentStatus.PENDING,
            Payment.due_date == reminder_date
        ).all()

        logger.info(f"Found {len(pending_payments)} payments requiring reminders")

        for payment in pending_payments:
            try:
                member = payment.member

                # Send email reminder
                notification_manager.send_email(
                    recipient=member.user.email,
                    subject="Payment Reminder - Due in 3 Days",
                    content=f"""
                    Hi {member.user.first_name},

                    This is a reminder that your payment of ${payment.amount} is due on {payment.due_date}.

                    Please ensure your payment method is up to date to avoid any interruption in your membership.

                    Thank you!
                    """
                )

                # Send SMS if phone number available
                if member.user.phone:
                    notification_manager.send_sms(
                        recipient=member.user.phone,
                        content=f"Payment reminder: ${payment.amount} due on {payment.due_date}. Update payment method if needed."
                    )

                logger.info(f"Payment reminder sent to member {member.id}")

            except Exception as e:
                logger.error(f"Error sending payment reminder for payment {payment.id}: {str(e)}")
                continue

        logger.info("Payment reminders sent successfully")

    except Exception as e:
        logger.error(f"Error in send_payment_reminders task: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.notifications.send_class_reminders")
def send_class_reminders():
    """Send reminders for upcoming classes"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        # Get classes starting in the next hour
        now = datetime.now()
        one_hour_later = now + timedelta(hours=1)

        upcoming_schedules = db.query(ClassSchedule).filter(
            ClassSchedule.scheduled_date == date.today(),
            ClassSchedule.status == ClassStatus.SCHEDULED
        ).all()

        logger.info(f"Found {len(upcoming_schedules)} scheduled classes today")

        for schedule in upcoming_schedules:
            try:
                # Check if class starts in the next hour
                class_datetime = datetime.combine(
                    schedule.scheduled_date,
                    schedule.start_time
                )

                # Only send reminder if class is 30 minutes away
                time_diff = class_datetime - now
                if timedelta(minutes=25) <= time_diff <= timedelta(minutes=35):
                    # Get all booked members
                    bookings = db.query(ClassBooking).filter(
                        ClassBooking.schedule_id == schedule.id,
                        ClassBooking.status == BookingStatus.BOOKED
                    ).all()

                    for booking in bookings:
                        try:
                            member = booking.member

                            # Send push notification if FCM token available
                            # TODO: Get FCM token from member
                            # notification_manager.send_push(...)

                            # Send email
                            notification_manager.send_email(
                                recipient=member.user.email,
                                subject=f"Class Reminder: {schedule.class_obj.name}",
                                content=f"""
                                Hi {member.user.first_name},

                                Your class "{schedule.class_obj.name}" starts in 30 minutes!

                                Time: {schedule.start_time}
                                Location: {schedule.class_obj.room}
                                Instructor: {schedule.instructor.user.first_name if schedule.instructor else 'TBA'}

                                See you there!
                                """
                            )

                            logger.info(f"Class reminder sent to member {member.id}")

                        except Exception as e:
                            logger.error(f"Error sending class reminder to member {booking.member_id}: {str(e)}")
                            continue

            except Exception as e:
                logger.error(f"Error processing class schedule {schedule.id}: {str(e)}")
                continue

        logger.info("Class reminders sent successfully")

    except Exception as e:
        logger.error(f"Error in send_class_reminders task: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.notifications.send_welcome_email")
def send_welcome_email(member_id: str):
    """Send welcome email to new member"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        from app.models.member import Member

        member = db.query(Member).filter(Member.id == member_id).first()

        if not member:
            logger.error(f"Member {member_id} not found")
            return

        notification_manager.send_email(
            recipient=member.user.email,
            subject="Welcome to FitFlow Pro!",
            content=f"""
            Hi {member.user.first_name},

            Welcome to FitFlow Pro! We're excited to have you as part of our community.

            Your member ID is: {member.member_id}

            You can now:
            - Check in at the gym using your QR code
            - Book classes through our mobile app
            - Track your progress and goals
            - Access all gym facilities

            Download our mobile app to get started!

            If you have any questions, feel free to reach out to our staff.

            Welcome aboard!
            The FitFlow Pro Team
            """
        )

        logger.info(f"Welcome email sent to member {member_id}")

    except Exception as e:
        logger.error(f"Error sending welcome email to member {member_id}: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.notifications.send_birthday_wishes")
def send_birthday_wishes():
    """Send birthday wishes to members"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        from app.models.member import Member

        today = date.today()

        # Get members with birthday today
        members = db.query(Member).filter(
            Member.date_of_birth != None
        ).all()

        birthday_members = [
            m for m in members
            if m.date_of_birth.month == today.month and m.date_of_birth.day == today.day
        ]

        logger.info(f"Found {len(birthday_members)} members with birthdays today")

        for member in birthday_members:
            try:
                notification_manager.send_email(
                    recipient=member.user.email,
                    subject="Happy Birthday from FitFlow Pro! 🎉",
                    content=f"""
                    Happy Birthday, {member.user.first_name}! 🎂

                    Wishing you a fantastic day filled with joy and celebration!

                    As a birthday gift from us, enjoy a complimentary guest pass to bring a friend to the gym this week!

                    Keep up the great work and have an amazing year ahead!

                    Best wishes,
                    The FitFlow Pro Team
                    """
                )

                logger.info(f"Birthday email sent to member {member.id}")

            except Exception as e:
                logger.error(f"Error sending birthday email to member {member.id}: {str(e)}")
                continue

        logger.info("Birthday wishes sent successfully")

    except Exception as e:
        logger.error(f"Error in send_birthday_wishes task: {str(e)}")
    finally:
        db.close()
