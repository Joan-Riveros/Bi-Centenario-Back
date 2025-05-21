from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from app.db.base import Base
from app.core.enums import UserRole 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    nombre = Column(String(100), nullable=False) 

    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.VISITANTE)
    #
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
    #
    #
    two_factor_setting = relationship(
        "User2FASetting",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )
    #two facotr
    @property
    def is_2fa_enabled(self) -> bool:
        """Determina si el usuario tiene 2FA habilitado."""
        if self.two_factor_setting:
            return self.two_factor_setting.is_enabled
        return False
    
    uploaded_documents = relationship(
        "Document",
        back_populates="uploader",
        cascade="all, delete-orphan",
    )
    upload_privilege_requests = relationship(
        "UploadPrivilegeRequest",
        back_populates="requester",
        cascade="all, delete-orphan" 
    )

    document_access_requests = relationship(
        "DocumentAccessRequest",
        back_populates="requester",
        cascade="all, delete-orphan" 
    )
    #collections
    collections = relationship(
        "Collection",
        back_populates="owner",
        cascade="all, delete-orphan" 
    )
    #rating
    ratings = relationship(
        "Rating",
        back_populates="rater",
        cascade="all, delete-orphan" 
    )
    #comments
    comments = relationship(
        "Comment",
        back_populates="commenter",
        cascade="all, delete-orphan" 
    )
