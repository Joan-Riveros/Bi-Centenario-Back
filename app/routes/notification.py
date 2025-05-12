from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/notifications", response_model=list[NotificationOut])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()


@router.post("/notifications/{notification_id}/mark-as-read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")

    notification.is_read = True
    db.commit()
    return {"detail": "Notificacion marcada como leida"}
