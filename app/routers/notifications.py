from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Notification, User
from app.schemas.notifications import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)

router = APIRouter()


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    """
    Create a notification for a user.
    """
    # Optional: ensure the target user exists (helpful for data integrity)
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")

    notif = Notification(
        user_id=payload.user_id,
        type=payload.type,
        message=payload.message,
        is_read=payload.is_read or False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    unread_only: Optional[bool] = Query(False, description="Only return unread notifications"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List notifications. Use query params to filter:
    - user_id: returns notifications for a specific user
    - unread_only: when True returns only unread notifications
    - pagination via skip & limit
    """
    q = db.query(Notification)
    if user_id is not None:
        q = q.filter(Notification.user_id == user_id)
    if unread_only:
        q = q.filter(Notification.is_read == False)  # noqa: E712

    q = q.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    results = q.all()
    return results


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single notification by id.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int, payload: NotificationUpdate, db: Session = Depends(get_db)
):
    """
    Update a notification (partial update). Typical use: mark as read/unread.
    """
    notif: Notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notif, field, value)

    db.commit()
    db.refresh(notif)
    return notif


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Delete a notification.
    """
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return None


@router.post("/bulk/mark-read", response_model=dict)
def bulk_mark_read(user_id: int, db: Session = Depends(get_db)):
    """
    Mark all notifications for a given user as read.
    Returns a small summary dict with how many were updated.
    """
    q = db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False)
    count = q.count()
    if count == 0:
        return {"updated": 0}
    q.update({Notification.is_read: True}, synchronize_session="fetch")
    db.commit()
    return {"updated": count}
