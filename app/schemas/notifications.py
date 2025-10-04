# app/schemas/notifications.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# ==========================================================
#                 NOTIFICATION SCHEMAS
# ==========================================================

class NotificationBase(BaseModel):
    user_id: int = Field(..., description="ID of the user receiving the notification")
    type: str = Field(default="info", description="info | warning | alert")
    message: str = Field(..., description="Notification message content")
    is_read: Optional[bool] = Field(default=False, description="Whether the notification has been read")


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification"""
    user_id: int
    message: str
    type: Optional[str] = "info"


class NotificationUpdate(BaseModel):
    """Schema for updating an existing notification"""
    is_read: Optional[bool] = Field(None, description="Mark notification as read or unread")
    message: Optional[str] = None
    type: Optional[str] = None


class NotificationResponse(NotificationBase):
    """Schema for returning notification data"""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
#             NESTED RELATIONSHIPS (OPTIONAL)
# ==========================================================

class UserWithNotifications(BaseModel):
    """Include notifications within a user response"""
    id: int
    full_name: str
    email: str
    notifications: List[NotificationResponse] = []

    model_config = ConfigDict(from_attributes=True)
