from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_default_admin():
    db: Session = SessionLocal()

    existing = db.query(User).filter(User.email == "admin@foro.com").first()
    if existing:
        db.close()
        return

    admin_user = User(
        email="admin@foro.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        role="admin"
    )

    db.add(admin_user)
    db.commit()
    db.close()
