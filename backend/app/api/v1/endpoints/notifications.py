from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    BulkNotificationCreate
)

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    notification_type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notifications for organization"""
    query = db.query(Notification).filter(
        Notification.organization_id == current_user.organization_id
    )

    if notification_type:
        query = query.filter(Notification.type == notification_type)

    if status:
        query = query.filter(Notification.status == status)

    if user_id:
        query = query.filter(Notification.user_id == user_id)

    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification"""
    notification = Notification(
        organization_id=current_user.organization_id,
        user_id=notification_in.user_id,
        type=notification_in.type,
        title=notification_in.title,
        body=notification_in.body,
        status="pending"
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    # TODO: Trigger notification sending based on type
    # from app.tasks.notifications import send_notification
    # send_notification.delay(notification.id)

    return notification


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_bulk_notifications(
    bulk_notification: BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notifications for multiple users"""
    notifications = []

    for user_id in bulk_notification.user_ids:
        notification = Notification(
            organization_id=current_user.organization_id,
            user_id=user_id,
            type=bulk_notification.type,
            title=bulk_notification.title,
            body=bulk_notification.body,
            status="pending"
        )
        notifications.append(notification)

    db.add_all(notifications)
    db.commit()

    # TODO: Trigger bulk notification sending
    # from app.tasks.notifications import send_bulk_notifications
    # send_bulk_notifications.delay([n.id for n in notifications])

    return {
        "message": f"Created {len(notifications)} notifications",
        "count": len(notifications)
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification by ID"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.organization_id == current_user.organization_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: UUID,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.organization_id == current_user.organization_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Update fields
    update_data = notification_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)

    db.commit()
    db.refresh(notification)

    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.organization_id == current_user.organization_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return None


@router.post("/send", status_code=status.HTTP_200_OK)
def send_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a notification immediately without storing"""
    # TODO: Implement immediate notification sending
    # This would use the notification service to send email/sms/push directly

    from app.services.notification import NotificationService

    notification_service = NotificationService()

    try:
        if notification_data.type == "email":
            # Send email
            pass
        elif notification_data.type == "sms":
            # Send SMS
            pass
        elif notification_data.type == "push":
            # Send push notification
            pass

        return {
            "message": "Notification sent successfully",
            "type": notification_data.type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.get("/templates/")
def get_notification_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification templates"""
    # TODO: Implement template management
    # For now, return predefined templates

    templates = {
        "welcome": {
            "title": "Welcome to {gym_name}!",
            "body": "Hi {member_name}, welcome to our gym! We're excited to have you.",
            "type": "email"
        },
        "payment_reminder": {
            "title": "Payment Reminder",
            "body": "Hi {member_name}, your payment of {amount} is due on {due_date}.",
            "type": "email"
        },
        "membership_expiry": {
            "title": "Membership Expiring Soon",
            "body": "Hi {member_name}, your membership expires on {expiry_date}. Please renew to continue.",
            "type": "email"
        },
        "class_reminder": {
            "title": "Class Reminder",
            "body": "Hi {member_name}, your class '{class_name}' starts in 30 minutes at {start_time}.",
            "type": "push"
        },
        "booking_confirmation": {
            "title": "Booking Confirmed",
            "body": "Hi {member_name}, your booking for '{class_name}' on {date} at {time} is confirmed!",
            "type": "push"
        }
    }

    return {"templates": templates}


@router.get("/history/")
def get_notification_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification history with analytics"""
    notifications = db.query(Notification).filter(
        Notification.organization_id == current_user.organization_id,
        Notification.status.in_(["sent", "failed"])
    ).order_by(Notification.sent_at.desc()).offset(skip).limit(limit).all()

    # Calculate stats
    total_sent = db.query(Notification).filter(
        Notification.organization_id == current_user.organization_id,
        Notification.status == "sent"
    ).count()

    total_failed = db.query(Notification).filter(
        Notification.organization_id == current_user.organization_id,
        Notification.status == "failed"
    ).count()

    return {
        "notifications": notifications,
        "stats": {
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0
        }
    }
