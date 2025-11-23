from celery import shared_task
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.payment import Payment, PaymentStatus
from app.models.membership import Membership, MembershipStatus
from app.services.payment_gateway import PaymentGatewayFactory
from app.services.notification import NotificationManager
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.payments.process_recurring_payments")
def process_recurring_payments():
    """Process recurring payments for active memberships"""
    db: Session = SessionLocal()
    notification_manager = NotificationManager()

    try:
        # Get all memberships due for renewal today
        today = date.today()
        due_memberships = db.query(Membership).filter(
            Membership.status == MembershipStatus.ACTIVE,
            Membership.auto_renew == True,
            Membership.end_date == today
        ).all()

        logger.info(f"Found {len(due_memberships)} memberships due for renewal")

        for membership in due_memberships:
            try:
                # Get member and plan details
                member = membership.member
                plan = membership.plan

                # Check for pending payment
                pending_payment = db.query(Payment).filter(
                    Payment.membership_id == membership.id,
                    Payment.status == PaymentStatus.PENDING,
                    Payment.due_date == today
                ).first()

                if pending_payment:
                    # Attempt to charge payment
                    payment_gateway = PaymentGatewayFactory.get_gateway("stripe")

                    # TODO: Get customer's saved payment method
                    # For now, create a payment record
                    pending_payment.retry_count += 1

                    # If max retries reached, send notification
                    if pending_payment.retry_count >= 3:
                        pending_payment.status = PaymentStatus.FAILED

                        # Send failure notification
                        notification_manager.send_email(
                            recipient=member.user.email,
                            subject="Payment Failed - Action Required",
                            content=f"Your membership renewal payment has failed. Please update your payment method."
                        )

                        # Freeze membership
                        membership.status = MembershipStatus.FROZEN
                        logger.warning(f"Membership {membership.id} frozen due to failed payment")
                    else:
                        # Schedule retry
                        retry_payment.apply_async(
                            args=[str(pending_payment.id)],
                            countdown=86400  # Retry after 24 hours
                        )

                    db.commit()

            except Exception as e:
                logger.error(f"Error processing payment for membership {membership.id}: {str(e)}")
                db.rollback()
                continue

        logger.info("Recurring payments processing completed")

    except Exception as e:
        logger.error(f"Error in process_recurring_payments task: {str(e)}")
    finally:
        db.close()


@shared_task(name="app.tasks.payments.retry_payment")
def retry_payment(payment_id: str):
    """Retry a failed payment"""
    db: Session = SessionLocal()

    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return

        if payment.status != PaymentStatus.PENDING:
            logger.info(f"Payment {payment_id} is not pending, skipping retry")
            return

        # Attempt payment
        payment_gateway = PaymentGatewayFactory.get_gateway(payment.payment_gateway or "stripe")

        # TODO: Implement actual payment retry logic
        # This is a placeholder

        payment.retry_count += 1
        db.commit()

        logger.info(f"Payment {payment_id} retry completed")

    except Exception as e:
        logger.error(f"Error retrying payment {payment_id}: {str(e)}")
        db.rollback()
    finally:
        db.close()


@shared_task(name="app.tasks.payments.generate_invoice_pdf")
def generate_invoice_pdf(invoice_id: str):
    """Generate PDF for an invoice"""
    db: Session = SessionLocal()

    try:
        from app.models.payment import Invoice

        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

        if not invoice:
            logger.error(f"Invoice {invoice_id} not found")
            return

        # TODO: Implement PDF generation logic
        # This would use a library like WeasyPrint or ReportLab

        logger.info(f"Invoice PDF generated for {invoice_id}")

    except Exception as e:
        logger.error(f"Error generating invoice PDF {invoice_id}: {str(e)}")
    finally:
        db.close()
