from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "fitflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Process recurring payments daily at 2 AM
    "process-recurring-payments": {
        "task": "app.tasks.payments.process_recurring_payments",
        "schedule": crontab(hour=2, minute=0),
    },
    # Send payment reminders daily at 9 AM
    "send-payment-reminders": {
        "task": "app.tasks.notifications.send_payment_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
    # Check expiring memberships daily at 8 AM
    "check-expiring-memberships": {
        "task": "app.tasks.memberships.check_expiring_memberships",
        "schedule": crontab(hour=8, minute=0),
    },
    # Send class reminders every hour
    "send-class-reminders": {
        "task": "app.tasks.notifications.send_class_reminders",
        "schedule": crontab(minute=0),  # Every hour
    },
    # Update analytics weekly on Sunday at 1 AM
    "update-analytics": {
        "task": "app.tasks.analytics.update_weekly_analytics",
        "schedule": crontab(hour=1, minute=0, day_of_week=0),
    },
    # Check inactive members weekly
    "check-inactive-members": {
        "task": "app.tasks.memberships.check_inactive_members",
        "schedule": crontab(hour=10, minute=0, day_of_week=1),  # Monday at 10 AM
    },
}

# Import tasks to register them
from app.tasks import payments, notifications, memberships, analytics
