from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.notification import NotificationType, NotificationStatus


# Notification Schemas
class NotificationBase(BaseModel):
    user_id: Optional[UUID] = None
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    sent_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    id: UUID
    organization_id: UUID
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Bulk Notification
class BulkNotificationCreate(BaseModel):
    user_ids: List[UUID] = Field(..., min_items=1)
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)


# Notification Template
class NotificationTemplate(BaseModel):
    name: str
    type: NotificationType
    title: str
    body: str
    variables: List[str] = Field(default_factory=list)


# Scheduled Notification
class ScheduledNotificationCreate(BaseModel):
    user_id: Optional[UUID] = None
    user_ids: Optional[List[UUID]] = None
    type: NotificationType
    title: str
    body: str
    scheduled_for: datetime


class ScheduledNotificationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: Optional[UUID] = None
    type: NotificationType
    title: str
    body: str
    scheduled_for: datetime
    status: str  # pending, sent, cancelled
    created_at: datetime

    class Config:
        from_attributes = True
