from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON 

from app.db.base import Base
from app.models.user import User

class User2FASetting(Base):
    __tablename__ = "user_2fa_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    
    encrypted_totp_secret = Column(LargeBinary, nullable=True)

    is_enabled = Column(Boolean, default=False, nullable=False)

    
    encrypted_backup_codes = Column(JSON, nullable=True) 

    
    user = relationship("User", back_populates="two_factor_setting")

    # Campos extra:
    # last_verified_at = Column(DateTime, nullable=True)
    # failed_attempts = Column(Integer, default=0, nullable=False)